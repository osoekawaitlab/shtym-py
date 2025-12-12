"""End-to-end tests for Ollama integration.

These tests verify basic Ollama integration functionality:
- Custom model specification via environment variables
- Fallback to PassThrough when model doesn't exist

These tests use ollama_recorder to verify actual HTTP requests.
"""

import json
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

from tests.e2e.helpers import JUDGE_MODEL, OllamaRecorder


def test_ollama_integration_with_custom_model(
    ollama_recorder: OllamaRecorder,
) -> None:
    """Verify custom model name is passed to Ollama API correctly.

    This test confirms that SHTYM_LLM_SETTINGS__MODEL is respected
    and the specified model name appears in the HTTP request to Ollama.
    """
    env = os.environ.copy()

    # Use recorder's proxy URL
    env["SHTYM_LLM_SETTINGS__BASE_URL"] = ollama_recorder.base_url
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

    recorded_requests = list(ollama_recorder.get_recorded_requests().values())
    chat_requests = [
        req for req in recorded_requests if req["request"]["path"] == "/api/chat"
    ]
    assert chat_requests, (
        "No /api/chat request found in recorded interactions; "
        f"paths seen: {sorted({req['request']['path'] for req in recorded_requests})}"
    )

    models = [json.loads(req["request"]["body"]).get("model") for req in chat_requests]
    assert JUDGE_MODEL in models, (
        f"Expected model '{JUDGE_MODEL}' in chat requests, got {models}"
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
