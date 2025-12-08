"""End-to-end tests for Ollama integration.

These tests verify basic Ollama integration functionality:
- Custom model specification via environment variables
- Fallback to PassThrough when model doesn't exist

These tests require Ollama to be running but do NOT use LLM-as-a-Judge.
They are suitable for CI/CD execution.
"""

import os
import subprocess

import pytest

pytest.importorskip(
    "ollama",
    reason=(
        "ollama package not installed; run 'pip install \"shtym[ollama]\"' "
        "to enable Ollama E2E tests."
    ),
)

from tests.e2e.test_ollama_judge import JUDGE_MODEL


@pytest.mark.requires_external_service
@pytest.mark.usefixtures("ollama_environment")
def test_ollama_integration_with_custom_model() -> None:
    """Run CLI with custom model specified via SHTYM_LLM_SETTINGS__MODEL."""
    env = os.environ.copy()

    # Use JUDGE_MODEL as custom model for testing
    env["SHTYM_LLM_SETTINGS__MODEL"] = JUDGE_MODEL

    test_input = "This is a test and you should summarize to 'T'"
    result = subprocess.run(  # noqa: S603
        ["stym", "run", "echo", test_input],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )

    # Verify command succeeded
    assert result.returncode == 0
    # Verify LLM processed the output (output should be different from input)
    assert result.stdout != f"{test_input}\n", (
        "Output should be processed by LLM, not passed through unchanged"
    )


@pytest.mark.requires_external_service
@pytest.mark.usefixtures("ollama_environment")
def test_ollama_integration_with_nonexistent_model_falls_back_to_passthrough() -> None:
    """Run CLI with non-existent model to verify fallback to PassThroughProcessor."""
    env = os.environ.copy()

    # Use a model name that definitely doesn't exist
    env["SHTYM_LLM_SETTINGS__MODEL"] = "definitely-nonexistent-model-12345"

    test_input = "Test output from command"
    result = subprocess.run(  # noqa: S603
        ["stym", "run", "echo", test_input],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )

    # Verify command succeeded
    assert result.returncode == 0
    # Verify output is passed through unchanged (fallback to PassThroughProcessor)
    assert test_input in result.stdout
