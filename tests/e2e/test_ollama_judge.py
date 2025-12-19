"""End-to-end tests using LLM-as-a-Judge.

These tests use a large LLM model to evaluate the quality of shtym's output.
They are expensive and require:
- SHTYMTEST_ENABLE_LLM_JUDGE environment variable to be set
- A large judge model (gpt-oss:120b) to be available in Ollama

These tests should typically be skipped in CI/CD environments and only
run during local development or manual testing.
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

from tests.e2e.helpers import OllamaJudge
from tests.fixtures import nox_pytest_failure_message


@pytest.mark.requires_external_service
def test_ollama_integration_when_enabled(ollama_judge: OllamaJudge) -> None:
    """Run CLI against a real Ollama instance and evaluate output quality.

    This test uses LLM-as-a-Judge to verify that shtym produces high-quality
    summaries. It requires SHTYMTEST_ENABLE_LLM_JUDGE to be set and is
    expensive to run.
    """
    env = os.environ.copy()

    result = subprocess.run(  # noqa: S603
        ["stym", "run", "echo", nox_pytest_failure_message],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )

    assert result.returncode == 0
    judge_result = ollama_judge.judge(
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
