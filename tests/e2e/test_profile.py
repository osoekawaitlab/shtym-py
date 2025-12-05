"""End-to-end tests for profile functionality."""

import os
import subprocess


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
