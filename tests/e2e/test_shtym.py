"""End-to-end tests for shtym."""

import re
import subprocess


def test_shtym_prints_version() -> None:
    """Test that shtym prints the version."""
    result = subprocess.run(
        ["stym", "--version"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert re.match(r"^\d+\.\d+\.\d+$", result.stdout.strip())
