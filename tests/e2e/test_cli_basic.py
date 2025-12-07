"""End-to-end tests for basic CLI functionality.

These tests verify core CLI behavior without LLM integration.
All tests disable LLM by setting BASE_URL to an invalid address.
"""

import os
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


def test_shtym_wrapper_inherits_exit_code_on_failure() -> None:
    """Test that shtym inherits the child process exit code when it fails."""
    result = subprocess.run(
        ["stym", "run", "false"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1


def test_shtym_wrapper_passes_command_options() -> None:
    """Test that shtym correctly passes options to the wrapped command."""
    env = os.environ.copy()
    env["SHTYM_LLM_SETTINGS__BASE_URL"] = "http://localhost:0000"  # Disable LLM calls
    result = subprocess.run(
        ["stym", "run", "ls", "-la"],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    # ls -la should include . and .. entries
    assert "." in result.stdout
    assert ".." in result.stdout
    assert result.returncode == 0


def test_shtym_wrapper_passes_help_flag_to_command() -> None:
    """Test that shtym passes --help to the command, not interpret it itself."""
    env = os.environ.copy()
    env["SHTYM_LLM_SETTINGS__BASE_URL"] = "http://localhost:0000"  # Disable LLM calls
    result = subprocess.run(
        ["stym", "run", "echo", "--help"],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    # echo treats --help as a regular argument and prints it
    assert "--help" in result.stdout
    assert result.returncode == 0


def test_shtym_wrapper_propagates_stderr() -> None:
    """Test that shtym propagates stderr from the child process."""
    result = subprocess.run(
        ["stym", "run", "python3", "-c", "import sys; sys.stderr.write('error\\n')"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.stderr == "error\n"
    assert result.returncode == 0
