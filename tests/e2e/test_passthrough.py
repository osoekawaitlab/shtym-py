"""Tests for shtym passthrough behavior."""

import os
import subprocess


def test_shtym_wrapper_passes_through_simple_command() -> None:
    """Test that shtym wraps a command and passes through its output."""
    env = os.environ.copy()
    env["SHTYM_LLM_SETTINGS__BASE_URL"] = "http://localhost:0000"  # Disable LLM calls
    result = subprocess.run(
        ["stym", "run", "echo", "test output"],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    assert result.stdout == "test output\n"
    assert result.stderr == ""
    assert result.returncode == 0
