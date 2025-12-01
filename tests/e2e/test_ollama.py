"""End-to-end tests for the CLI with and without Ollama."""

import os
import subprocess

import pytest


@pytest.mark.ollama
def test_ollama_integration_when_enabled() -> None:
    """Run CLI against a real Ollama instance when explicitly enabled."""
    env = os.environ.copy()
    env.setdefault("SHTYM_LLM_SETTINGS__BASE_URL", "http://localhost:11434")

    result = subprocess.run(
        ["stym", "run", "echo", "--help"],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )

    assert result.returncode == 0
    assert "--help" in result.stdout
