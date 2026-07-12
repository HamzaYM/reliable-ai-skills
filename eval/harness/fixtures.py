"""Fixture build, tree hashing, manifest verification, workspace staging.

A fixture is a directory under eval/fixtures/<name>/ with:
  build.sh       constructs a workspace deterministically: bash build.sh <dest>
  manifest.json  expected tree hash (working files, git internals excluded)
                 and expected git refs for every repo the build creates

Determinism contract: build.sh pins GIT_AUTHOR_* and GIT_COMMITTER_* (name,
email, date) for every commit, so SHAs are identical on every machine. The
harness additionally neutralizes user/system git config when running builds.
"""
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from . import FIXTURES_DIR


class FixtureError(Exception):
    pass


def _build_env():
    env = dict(os.environ)
    env.update(
        {
            "GIT_CONFIG_GLOBAL": "/dev/null",
            "GIT_CONFIG_SYSTEM": "/dev/null",
            "GIT_CONFIG_NOSYSTEM": "1",
            "TZ": "UTC",
            "LC_ALL": "C",
        }
    )
    return env


def build_fixture(name, dest):
    """Run the fixture's build.sh into dest (created if missing)."""
    script = FIXTURES_DIR / name / "build.sh"
    if not script.is_file():
        raise FixtureError(f"fixture {name}: missing build.sh")
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        ["bash", str(script), str(dest)],
        env=_build_env(),
        capture_output=True,
        text=True,
        timeout=120,
    )
    if proc.returncode != 0:
        raise FixtureError(
            f"fixture {name}: build.sh failed (exit {proc.returncode})\n"
            f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
        )
    return dest


def _is_bare_repo(path):
    return (path / "HEAD").is_file() and (path / "objects").is_dir()


def tree_hash(root):
    """SHA-256 over sorted (relative path, content) pairs.

    Git internals are excluded: `.git` directories always, and `*.git`
    directories only when they are real bare repos (covered by git_heads).
    A plain directory that merely ends in `.git` is hashed like any other.
    Symlinks are hashed by their link target (never followed), so
    retargeting one changes the hash.
    """
    root = Path(root)
    entries = []
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dpath = Path(dirpath)
        kept = []
        for d in dirnames:
            p = dpath / d
            if d == ".git" or (d.endswith(".git") and _is_bare_repo(p)):
                continue
            if p.is_symlink():
                entries.append(
                    (p.relative_to(root),
                     b"symlink\0" + os.readlink(p).encode("utf-8"))
                )
                continue
            kept.append(d)
        dirnames[:] = kept
        for f in filenames:
            p = dpath / f
            rel = p.relative_to(root)
            if p.is_symlink():
                entries.append(
                    (rel, b"symlink\0" + os.readlink(p).encode("utf-8"))
                )
            else:
                entries.append((rel, p.read_bytes()))
    h = hashlib.sha256()
    for rel, content in sorted(entries, key=lambda e: str(e[0])):
        h.update(str(rel).encode("utf-8"))
        h.update(b"\0")
        h.update(content)
        h.update(b"\0")
    return h.hexdigest()


def find_git_repos(root):
    """Relative paths of git repos (working clones and bare repos) under root."""
    root = Path(root)
    repos = []
    for p in sorted(root.rglob("*")):
        if not p.is_dir():
            continue
        rel = p.relative_to(root)
        if any(part == ".git" for part in rel.parts):
            continue  # never treat a repo's own .git dir as a bare repo
        if (p / ".git").is_dir():
            repos.append(str(rel))
        elif p.name.endswith(".git") and _is_bare_repo(p):
            repos.append(str(rel))
    return repos


def git_heads(repo_path):
    """{ref: sha} for every ref, plus the symbolic HEAD target."""
    out = subprocess.run(
        ["git", "-C", str(repo_path), "for-each-ref",
         "--format=%(refname) %(objectname)"],
        capture_output=True, text=True, env=_build_env(), check=True,
    ).stdout
    refs = {}
    for line in out.splitlines():
        name, sha = line.rsplit(" ", 1)
        refs[name] = sha
    head = subprocess.run(
        ["git", "-C", str(repo_path), "symbolic-ref", "-q", "HEAD"],
        capture_output=True, text=True, env=_build_env(),
    )
    if head.returncode == 0:
        refs["HEAD"] = f"ref: {head.stdout.strip()}"
    else:
        sha = subprocess.run(
            ["git", "-C", str(repo_path), "rev-parse", "HEAD"],
            capture_output=True, text=True, env=_build_env(), check=True,
        ).stdout.strip()
        refs["HEAD"] = sha
    return refs


def snapshot(workspace):
    """Tree hash plus git refs for every repo in a built workspace."""
    ws = Path(workspace)
    return {
        "tree_sha256": tree_hash(ws),
        "git_heads": {rel: git_heads(ws / rel) for rel in find_git_repos(ws)},
    }


def load_manifest(name):
    path = FIXTURES_DIR / name / "manifest.json"
    if not path.is_file():
        raise FixtureError(f"fixture {name}: missing manifest.json")
    return json.loads(path.read_text(encoding="utf-8"))


def write_manifest(name, extra=None):
    """Build the fixture in a temp dir and write its manifest.json.

    Maintenance helper for fixture authors; see eval/README.md.
    """
    with tempfile.TemporaryDirectory(prefix=f"fixture-{name}-") as tmp:
        ws = build_fixture(name, Path(tmp) / "ws")
        data = snapshot(ws)
    path = FIXTURES_DIR / name / "manifest.json"
    if path.exists():
        # preserve hand-authored fields (description, fake_ticket_prefixes, ...)
        # so regenerating only refreshes the computed snapshot values
        existing = json.loads(path.read_text(encoding="utf-8"))
        computed = set(data)
        data = {**{k: v for k, v in existing.items() if k not in computed}, **data}
    if extra:
        data.update(extra)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return data


def verify_fixture(name):
    """Rebuild the fixture and diff against manifest.json. Returns error strings."""
    errs = []
    try:
        manifest = load_manifest(name)
    except FixtureError as exc:
        return [str(exc)]
    with tempfile.TemporaryDirectory(prefix=f"fixture-{name}-") as tmp:
        try:
            ws = build_fixture(name, Path(tmp) / "ws")
        except FixtureError as exc:
            return [str(exc)]
        actual = snapshot(ws)
    if actual["tree_sha256"] != manifest.get("tree_sha256"):
        errs.append(
            f"fixture {name}: tree hash mismatch: rebuilt {actual['tree_sha256']}"
            f" != manifest {manifest.get('tree_sha256')}"
        )
    if actual["git_heads"] != manifest.get("git_heads"):
        errs.append(
            f"fixture {name}: git refs mismatch:\n"
            f"  rebuilt:  {json.dumps(actual['git_heads'], sort_keys=True)}\n"
            f"  manifest: {json.dumps(manifest.get('git_heads'), sort_keys=True)}"
        )
    return errs


def stage_workspace(built_fixture_dir, dest):
    """Copy a built fixture into a disposable per-run workspace."""
    shutil.copytree(built_fixture_dir, dest, symlinks=True)
    return Path(dest)


def install_skill(workspace, skill_dir, skill_name):
    """Copy the skill folder into <workspace>/.claude/skills/<skill_name>/."""
    target = Path(workspace) / ".claude" / "skills" / skill_name
    shutil.copytree(skill_dir, target)
    return target
