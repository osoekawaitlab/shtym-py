"""Tests for shtym passthrough behavior.

These tests verify that shtym correctly passes through command output
in various scenarios:
- LLM disabled
- Profile argument parsing
- Nonexistent profile fallback
"""

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


def test_profile_argument_is_accepted() -> None:
    """Test that --profile argument is accepted by CLI parser."""
    env = os.environ.copy()
    env["SHTYM_LLM_SETTINGS__BASE_URL"] = "http://localhost:0000"  # Disable LLM

    result = subprocess.run(
        ["stym", "run", "--profile", "default", "echo", "test"],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )

    # Should not fail with argument parsing error
    assert result.returncode == 0
    assert "test" in result.stdout


def test_nonexistent_profile_falls_back_to_passthrough() -> None:
    """Test that specifying non-existent profile falls back to PassThrough mode."""
    env = os.environ.copy()
    env["SHTYM_LLM_SETTINGS__BASE_URL"] = "http://localhost:11434"  # Valid Ollama
    env["SHTYM_LLM_SETTINGS__MODEL"] = "gpt-oss:20b"

    test_input = "This is a test and you should summarize to 'T'"
    result = subprocess.run(  # noqa: S603
        ["stym", "run", "--profile", "nonexistent", "echo", test_input],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )

    # Should succeed and return raw output (PassThrough) - exact match
    assert result.returncode == 0
    assert result.stdout == f"{test_input}\n"
