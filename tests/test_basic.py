"""Test the package entry point."""

import shutil
import subprocess

ENTRY_POINT = "pocketbudget"


def test_entry_point_prints_startup_message() -> None:
    executable = shutil.which(ENTRY_POINT)
    assert executable is not None, "pocketbudget console script is not installed"

    result = subprocess.run([executable], capture_output=True, text=True)

    assert result.returncode == 0
    assert "Hello PocketBudget" in result.stdout
    assert result.stderr == ""
