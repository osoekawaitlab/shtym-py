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


def test_shtym_wrapper_passes_through_simple_command() -> None:
    """Test that shtym wraps a command and passes through its output."""
    result = subprocess.run(
        ["stym", "run", "echo", "test output"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.stdout == "test output\n"
    assert result.stderr == ""
    assert result.returncode == 0


def test_shtym_wrapper_inherits_exit_code_on_failure() -> None:
    """Test that shtym inherits the child process exit code when it fails."""
    result = subprocess.run(
        ["stym", "run", "false"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.stdout == ""
    assert result.stderr == ""
    assert result.returncode == 1


def test_shtym_wrapper_passes_command_options() -> None:
    """Test that shtym correctly passes options to the wrapped command."""
    result = subprocess.run(
        ["stym", "run", "ls", "-la"],
        capture_output=True,
        text=True,
        check=False,
    )
    # ls -la should include . and .. entries
    assert "." in result.stdout
    assert ".." in result.stdout
    assert result.returncode == 0


def test_shtym_wrapper_passes_help_flag_to_command() -> None:
    """Test that shtym passes --help to the command, not interpret it itself."""
    result = subprocess.run(
        ["stym", "run", "echo", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    # echo treats --help as a regular argument and prints it
    assert "--help" in result.stdout
    assert result.returncode == 0
