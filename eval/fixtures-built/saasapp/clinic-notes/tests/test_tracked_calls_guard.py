import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_tracked_call_sites_unchanged():
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check_tracked_calls.py")],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
