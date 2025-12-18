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
    recorded_requests = list(ollama_recorder.get_observed_requests().values())
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


def test_override_default_profile_from_toml_file(
    tmp_path: Path, ollama_recorder: OllamaRecorder
) -> None:
    """Test that default profile can be overridden in profiles.toml.

    This verifies the merge behavior where profiles.toml overrides the
    hardcoded default profile that reads from environment variables.
    """
    # Create config directory structure
    config_dir = tmp_path / ".config" / "shtym"
    config_dir.mkdir(parents=True)
    profiles_file = config_dir / "profiles.toml"

    # Write profiles.toml that overrides the default profile
    profiles_file.write_text(
        f"""
[profiles.default]
type = "llm"
prompt_template = "CUSTOM DEFAULT: $command"

[profiles.default.llm_settings]
model_name = "{JUDGE_MODEL}"
base_url = "{ollama_recorder.base_url}"
""",
        encoding="utf-8",
    )

    # Set HOME to use temporary directory
    env = os.environ.copy()
    env["HOME"] = str(tmp_path)

    # Run shtym with --profile default (explicit)
    test_input = "test message"
    result = subprocess.run(  # noqa: S603
        ["stym", "run", "--profile", "default", "echo", test_input],
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

    # Verify LLM was called (overridden default uses LLM, not env vars)
    recorded_requests = list(ollama_recorder.get_observed_requests().values())
    chat_requests = [
        req for req in recorded_requests if req["request"]["path"] == "/api/chat"
    ]
    assert chat_requests, (
        "Expected /api/chat request for overridden default profile; "
        f"paths seen: {sorted({req['request']['path'] for req in recorded_requests})}\n"
        f"stdout: {result.stdout}\n"
        f"stderr: {result.stderr}"
    )

    # Verify custom prompt template is applied
    request_bodies = [json.loads(req["request"]["body"]) for req in chat_requests]
    messages_list = [body.get("messages", []) for body in request_bodies]

    expected_prompt_prefix = "CUSTOM DEFAULT:"
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
        f"from overridden default; messages: {messages_list}"
    )


def test_use_hardcoded_default_when_toml_file_missing(tmp_path: Path) -> None:
    """Test that hardcoded default profile is used when profiles.toml doesn't exist.

    This verifies backward compatibility - when no profiles.toml exists,
    the system should use the hardcoded default profile that reads from
    environment variables.
    """
    # Don't create profiles.toml - test missing file scenario
    env = os.environ.copy()
    env["HOME"] = str(tmp_path)

    # Run shtym with default profile
    test_input = "test message"
    result = subprocess.run(  # noqa: S603
        ["stym", "run", "--profile", "default", "echo", test_input],
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

    # Without profiles.toml, default profile uses environment variables
    # which are not configured in this test, so it should fall back to
    # PassThroughProcessor and just output the command result
    assert test_input in result.stdout, (
        f"Expected pass-through output '{test_input}' when using "
        f"hardcoded default without LLM config; got: {result.stdout}"
    )


def test_multiple_profiles_work_independently(
    tmp_path: Path, ollama_recorder: OllamaRecorder
) -> None:
    """Test that multiple profiles can be defined and used independently.

    This verifies that:
    1. Multiple profiles can coexist in profiles.toml
    2. Each profile maintains its own configuration
    3. Selecting a profile applies only its settings
    """
    # Create config directory structure
    config_dir = tmp_path / ".config" / "shtym"
    config_dir.mkdir(parents=True)
    profiles_file = config_dir / "profiles.toml"

    # Write profiles.toml with three different profiles
    profiles_file.write_text(
        f"""
[profiles.summary]
type = "llm"
prompt_template = "SUMMARIZE: $command"

[profiles.summary.llm_settings]
model_name = "{JUDGE_MODEL}"
base_url = "{ollama_recorder.base_url}"

[profiles.translate]
type = "llm"
prompt_template = "TRANSLATE: $command"

[profiles.translate.llm_settings]
model_name = "{JUDGE_MODEL}"
base_url = "{ollama_recorder.base_url}"

[profiles.explain]
type = "llm"
prompt_template = "EXPLAIN: $command"

[profiles.explain.llm_settings]
model_name = "{JUDGE_MODEL}"
base_url = "{ollama_recorder.base_url}"
""",
        encoding="utf-8",
    )

    # Set HOME to use temporary directory
    env = os.environ.copy()
    env["HOME"] = str(tmp_path)

    test_input = "test"

    # Test each profile independently
    profiles_to_test = [
        ("summary", "SUMMARIZE:"),
        ("translate", "TRANSLATE:"),
        ("explain", "EXPLAIN:"),
    ]

    for profile_name, expected_prefix in profiles_to_test:
        # Clear observed requests for clean test
        ollama_recorder.clear_observed_requests()

        result = subprocess.run(  # noqa: S603
            ["stym", "run", "--profile", profile_name, "echo", test_input],
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )

        assert result.returncode == 0, (
            f"Command failed for profile '{profile_name}' "
            f"with return code {result.returncode}\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        # Verify correct prompt template was used
        recorded_requests = list(ollama_recorder.get_observed_requests().values())
        chat_requests = [
            req for req in recorded_requests if req["request"]["path"] == "/api/chat"
        ]

        assert chat_requests, (
            f"Expected /api/chat request for profile '{profile_name}'; "
            f"paths seen: "
            f"{sorted({req['request']['path'] for req in recorded_requests})}"
        )

        request_bodies = [json.loads(req["request"]["body"]) for req in chat_requests]
        messages_list = [body.get("messages", []) for body in request_bodies]

        found_prefix = False
        for messages in messages_list:
            for message in messages:
                content = message.get("content", "")
                if expected_prefix in content:
                    found_prefix = True
                    break
            if found_prefix:
                break

        assert found_prefix, (
            f"Expected prompt prefix '{expected_prefix}' for profile "
            f"'{profile_name}'; messages: {messages_list}"
        )


def test_invalid_toml_syntax_falls_back_gracefully(tmp_path: Path) -> None:
    """Test that invalid TOML syntax silently falls back to default profile.

    Per ADR-0011: When profiles.toml contains syntax errors, silently fall back
    to PassThroughProcessor without warnings or errors. This maintains
    zero-configuration default behavior.
    """
    # Create config directory structure
    config_dir = tmp_path / ".config" / "shtym"
    config_dir.mkdir(parents=True)
    profiles_file = config_dir / "profiles.toml"

    # Write invalid TOML (missing closing bracket)
    profiles_file.write_text(
        """
[profiles.summary
type = "llm"
prompt_template = "Test"
""",
        encoding="utf-8",
    )

    # Set HOME to use temporary directory
    env = os.environ.copy()
    env["HOME"] = str(tmp_path)

    # Run shtym - should succeed with silent fallback
    test_input = "test message"
    result = subprocess.run(  # noqa: S603
        ["stym", "run", "--profile", "summary", "echo", test_input],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )

    # Verify the command succeeds (silent fallback to PassThrough)
    assert result.returncode == 0, (
        f"Expected silent fallback with zero exit code, got {result.returncode}\n"
        f"stdout: {result.stdout}\n"
        f"stderr: {result.stderr}"
    )

    # Verify pass-through behavior (output unchanged)
    assert test_input in result.stdout, (
        f"Expected pass-through output '{test_input}' after silent fallback; "
        f"got: {result.stdout}"
    )

    # Verify silent fallback (no error messages in stderr per ADR-0011)
    # Note: This is the current behavior; future --verbose flag may add notifications
    assert result.stderr == "", (
        f"Expected silent fallback with no stderr per ADR-0011; got: {result.stderr}"
    )


def test_missing_required_fields_in_profile(tmp_path: Path) -> None:
    """Test that invalid field types silently fall back to default profile.

    Per ADR-0011: When a profile has invalid field types (e.g., base_url is not
    a valid URL), Pydantic validation fails but the system silently falls back
    to PassThroughProcessor without warnings or errors.
    """
    # Create config directory structure
    config_dir = tmp_path / ".config" / "shtym"
    config_dir.mkdir(parents=True)
    profiles_file = config_dir / "profiles.toml"

    # Write profile with invalid base_url (not a valid URL)
    profiles_file.write_text(
        """
[profiles.invalid]
type = "llm"
prompt_template = "Test: $command"

[profiles.invalid.llm_settings]
model_name = "test-model"
base_url = "not-a-valid-url"
""",
        encoding="utf-8",
    )

    # Set HOME to use temporary directory
    env = os.environ.copy()
    env["HOME"] = str(tmp_path)

    # Run shtym - should succeed with silent fallback
    test_input = "test message"
    result = subprocess.run(  # noqa: S603
        ["stym", "run", "--profile", "invalid", "echo", test_input],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )

    # Verify the command succeeds (silent fallback to PassThrough)
    assert result.returncode == 0, (
        f"Expected silent fallback with zero exit code, got {result.returncode}\n"
        f"stdout: {result.stdout}\n"
        f"stderr: {result.stderr}"
    )

    # Verify pass-through behavior (output unchanged)
    assert test_input in result.stdout, (
        f"Expected pass-through output '{test_input}' after silent fallback; "
        f"got: {result.stdout}"
    )

    # Verify silent fallback (no error messages in stderr per ADR-0011)
    assert result.stderr == "", (
        f"Expected silent fallback with no stderr per ADR-0011; got: {result.stderr}"
    )


def test_use_default_profile_when_no_profile_specified(
    tmp_path: Path, ollama_recorder: OllamaRecorder
) -> None:
    """Test that default profile is used when --profile is not specified.

    When profiles.toml defines a custom default profile and the user
    doesn't specify --profile, the custom default should be used automatically.
    """
    # Create config directory structure
    config_dir = tmp_path / ".config" / "shtym"
    config_dir.mkdir(parents=True)
    profiles_file = config_dir / "profiles.toml"

    # Write profiles.toml with custom default and other profiles
    profiles_file.write_text(
        f"""
[profiles.default]
type = "llm"
prompt_template = "AUTO DEFAULT: $command"

[profiles.default.llm_settings]
model_name = "{JUDGE_MODEL}"
base_url = "{ollama_recorder.base_url}"

[profiles.other]
type = "llm"
prompt_template = "OTHER: $command"

[profiles.other.llm_settings]
model_name = "{JUDGE_MODEL}"
base_url = "{ollama_recorder.base_url}"
""",
        encoding="utf-8",
    )

    # Set HOME to use temporary directory
    env = os.environ.copy()
    env["HOME"] = str(tmp_path)

    # Run shtym WITHOUT --profile argument
    test_input = "test message"
    result = subprocess.run(  # noqa: S603
        ["stym", "run", "echo", test_input],  # No --profile specified
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

    # Verify LLM was called with default profile
    recorded_requests = list(ollama_recorder.get_observed_requests().values())
    chat_requests = [
        req for req in recorded_requests if req["request"]["path"] == "/api/chat"
    ]
    assert chat_requests, (
        "Expected /api/chat request for auto-selected default profile; "
        f"paths seen: {sorted({req['request']['path'] for req in recorded_requests})}\n"
        f"stdout: {result.stdout}\n"
        f"stderr: {result.stderr}"
    )

    # Verify default profile's custom prompt template is applied
    request_bodies = [json.loads(req["request"]["body"]) for req in chat_requests]
    messages_list = [body.get("messages", []) for body in request_bodies]

    expected_prompt_prefix = "AUTO DEFAULT:"
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
        f"Expected custom prompt '{expected_prompt_prefix}' from auto-selected "
        f"default; messages: {messages_list}"
    )
