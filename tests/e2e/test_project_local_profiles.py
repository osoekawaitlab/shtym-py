"""End-to-end tests for project-local profile configuration.

Tests the feature where profiles can be loaded from .shtym/profiles.toml
in the current directory, with priority: project local → user config → default.
"""

import json
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


def test_load_profile_from_project_local_directory(
    tmp_path: Path, ollama_recorder: OllamaRecorder
) -> None:
    """Test loading a profile from .shtym/profiles.toml in project directory.

    This test verifies that:
    1. Profiles can be loaded from .shtym/profiles.toml in current directory
    2. Project-local profiles work the same as user config profiles
    """
    # Create project directory with .shtym subdirectory
    project_dir = tmp_path / "my-project"
    project_dir.mkdir()
    shtym_dir = project_dir / ".shtym"
    shtym_dir.mkdir()

    # Write .shtym/profiles.toml with a custom profile
    profiles_file = shtym_dir / "profiles.toml"
    profiles_file.write_text(
        f"""
[profiles.project-profile]
type = "llm"
system_prompt_template = "PROJECT PROFILE: $command"
user_prompt_template = "$stdout"

[profiles.project-profile.llm_settings]
model_name = "{JUDGE_MODEL}"
base_url = "{ollama_recorder.base_url}"
""",
        encoding="utf-8",
    )

    # Run shtym from project directory with --profile project-profile
    test_input = "test message"
    result = subprocess.run(  # noqa: S603
        ["stym", "run", "--profile", "project-profile", "echo", test_input],
        capture_output=True,
        text=True,
        check=False,
        cwd=project_dir,  # Run from project directory
    )

    # Verify command succeeded
    assert result.returncode == 0, (
        f"Command failed with return code {result.returncode}\n"
        f"stdout: {result.stdout}\n"
        f"stderr: {result.stderr}"
    )

    # Verify LLM was called with the project profile's configuration
    recorded_requests = list(ollama_recorder.get_observed_requests().values())
    chat_requests = [
        req for req in recorded_requests if req["request"]["path"] == "/api/chat"
    ]
    assert chat_requests, (
        "Expected /api/chat request for project-local profile; "
        f"paths seen: {sorted({req['request']['path'] for req in recorded_requests})}\n"
        f"stdout: {result.stdout}\n"
        f"stderr: {result.stderr}"
    )

    # Verify project profile's custom prompt template is applied
    request_bodies = [json.loads(req["request"]["body"]) for req in chat_requests]
    messages_list = [body.get("messages", []) for body in request_bodies]

    expected_prompt_prefix = "PROJECT PROFILE:"
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
        f"from project-local profile; messages: {messages_list}"
    )
