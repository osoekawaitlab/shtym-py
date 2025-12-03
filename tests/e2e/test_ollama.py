"""End-to-end tests for the CLI with and without Ollama."""

import os
import subprocess

import pytest

from tests.e2e.helpers import OllamaJudge
from tests.fixtures import nox_pytest_failure_message


@pytest.mark.ollama
def test_ollama_integration_when_enabled() -> None:
    """Run CLI against a real Ollama instance when explicitly enabled."""
    env = os.environ.copy()
    assert env.get("SHTYM_LLM_SETTINGS__BASE_URL") is not None
    judge = OllamaJudge.create(base_url=env["SHTYM_LLM_SETTINGS__BASE_URL"])

    result = subprocess.run(  # noqa: S603
        ["stym", "run", "echo", nox_pytest_failure_message],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )

    assert result.returncode == 0
    judge_result = judge.judge(
        prompt="Did the output contain a pytest failure message?",
        response=result.stdout,
    )
    score_threshold = 0.9
    assert judge_result.score >= score_threshold, (
        f"Low score: {judge_result.score}, feedback: {judge_result.feedback}"
    )
    confidence_threshold = 0.7
    assert judge_result.confidence >= confidence_threshold, (
        f"Low confidence: {judge_result.confidence}, feedback: {judge_result.feedback}"
    )
