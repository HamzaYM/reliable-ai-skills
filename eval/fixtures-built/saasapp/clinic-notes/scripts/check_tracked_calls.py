#!/usr/bin/env python3
"""Guard: verify the tracked LLM call sites are unchanged.

Walks every *.py file in the repo, collects the file:line of each match of
the literal receiver pattern `tracked_client.complete(`, and compares that
set against scripts/tracked_baseline.txt. Exit 0 when they are equal.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
PATTERN = re.compile(r"\btracked_client\.complete\(")


def current_call_sites():
    sites = set()
    for path in sorted(ROOT.rglob("*.py")):
        if ".git" in path.parts or path.name == "check_tracked_calls.py":
            continue
        for lineno, line in enumerate(
                path.read_text(encoding="utf-8").splitlines(), start=1):
            if PATTERN.search(line):
                sites.add(f"{path.relative_to(ROOT)}:{lineno}")
    return sites


def main():
    baseline_path = ROOT / "scripts" / "tracked_baseline.txt"
    expected = {
        line.strip()
        for line in baseline_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }
    actual = current_call_sites()
    if actual == expected:
        print("tracked call sites unchanged")
        return 0
    for missing in sorted(expected - actual):
        print(f"missing tracked call site: {missing}")
    for added in sorted(actual - expected):
        print(f"new tracked call site not in the recorded list: {added}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
