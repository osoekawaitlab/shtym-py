"""End-to-end tests for loading profiles from ~/.config/shtym/profiles.toml."""

import json
import os
import subprocess
from pathlib import Path

import pytest

pytest.importorskip(
    "ollama",
    reason=(
        "ollama package not installed; run 'pip install \"shtym[ollama]\"' "
        "to enable Ollama E2E tests."
    ),
)

from tests.e2e.helpers import JUDGE_MODEL, OllamaRecorder


def test_load_profile_from_toml_file(
    tmp_path: Path, ollama_recorder: OllamaRecorder
) -> None:
    """Test loading a custom profile from profiles.toml file.

    This test verifies that:
    1. Custom profiles can be loaded from ~/.config/shtym/profiles.toml
    2. Profile settings (prompt_template, model_name, base_url) are applied
    3. The LLM is called with the profile's configuration
    """
    # Create config directory structure
    config_dir = tmp_path / ".config" / "shtym"
    config_dir.mkdir(parents=True)
    profiles_file = config_dir / "profiles.toml"

    # Write profiles.toml with a custom profile
    profiles_file.write_text(
        f"""
[profiles.summary]
type = "llm"
prompt_template = "Summarize this in one word: $command"

[profiles.summary.llm_settings]
model_name = "{JUDGE_MODEL}"
base_url = "{ollama_recorder.base_url}"
""",
        encoding="utf-8",
    )

    # Set HOME to use temporary directory
    env = os.environ.copy()
    env["HOME"] = str(tmp_path)

    # Run shtym with --profile summary
    test_input = "This is a test message"
    result = subprocess.run(  # noqa: S603
        ["stym", "run", "--profile", "summary", "echo", test_input],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )

    # Verify command succeeded
    assert result.returncode == 0, (
        f"Command failed with return code {result.returncode}\n"
        f"stdout: {result.stdout}\n"
        f"stderr: {result.stderr}"
    )

    # Verify LLM was called with the profile's configuration
    recorded_requests = list(ollama_recorder.get_recorded_requests().values())
    chat_requests = [
        req for req in recorded_requests if req["request"]["path"] == "/api/chat"
    ]
    assert chat_requests, (
        "Expected /api/chat request for profile-based LLM processing; "
        f"paths seen: {sorted({req['request']['path'] for req in recorded_requests})}\n"
        f"stdout: {result.stdout}\n"
        f"stderr: {result.stderr}"
    )

    # Verify model name is JUDGE_MODEL from profile configuration
    models = [json.loads(req["request"]["body"]).get("model") for req in chat_requests]
    assert JUDGE_MODEL in models, (
        f"Expected model '{JUDGE_MODEL}' from profile configuration, got {models}"
    )

    # Verify prompt template is applied (should contain the custom prompt)
    # The prompt template is "Summarize this in one word: $command"
    # where $command is replaced with the actual command output
    request_bodies = [json.loads(req["request"]["body"]) for req in chat_requests]
    messages_list = [body.get("messages", []) for body in request_bodies]

    # Check that the custom prompt appears in the messages
    expected_prompt_prefix = "Summarize this in one word:"
    found_custom_prompt = False
    for messages in messages_list:
        for message in messages:
            content = message.get("content", "")
            if expected_prompt_prefix in content:
                found_custom_prompt = True
                break
        if found_custom_prompt:
            break

    assert found_custom_prompt, (
        f"Expected custom prompt '{expected_prompt_prefix}' "
        f"from profile configuration; messages: {messages_list}"
    )
