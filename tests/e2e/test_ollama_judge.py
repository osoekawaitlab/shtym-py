"""End-to-end tests using LLM-as-a-Judge.

These tests use a large LLM model to evaluate the quality of shtym's output.
They are expensive and require:
- SHTYMTEST_ENABLE_LLM_JUDGE environment variable to be set
- A large judge model (gpt-oss:120b) to be available in Ollama

These tests should typically be skipped in CI/CD environments and only
run during local development or manual testing.
"""

import json
import os
import subprocess
from dataclasses import dataclass

import pytest

pytest.importorskip(
    "ollama",
    reason=(
        "ollama package not installed; run 'pip install \"shtym[ollama]\"' "
        "to enable Ollama E2E tests."
    ),
)

from ollama import Client, Message

from tests.fixtures import nox_pytest_failure_message


@dataclass
class JudgementResult:
    """Result of a judgement."""

    score: float
    confidence: float
    feedback: str


JUDGE_MODEL = "gpt-oss:120b"

judgement_result_schema = {
    "title": "JudgementResult",
    "type": "object",
    "properties": {
        "score": {"type": "number"},
        "confidence": {"type": "number"},
        "feedback": {"type": "string"},
    },
    "required": ["score", "confidence", "feedback"],
    "additionalProperties": False,
}


class OllamaJudge:
    """Helper class to use Ollama as a judge in end-to-end tests."""

    def __init__(self, client: Client) -> None:
        """Initialize the Ollama client."""
        self.client = client

    @classmethod
    def create(cls, base_url: str) -> "OllamaJudge":
        """Create an OllamaJudge with the specified base URL."""
        client = Client(host=base_url)
        model_names = [m.model for m in client.list().models]
        assert JUDGE_MODEL in model_names, (
            f"Model {JUDGE_MODEL} not found in Ollama instance."
        )
        return cls(client)

    def judge(self, prompt: str, response: str) -> JudgementResult:
        """Use Ollama to judge the response based on the prompt."""
        full_prompt = (
            "You are an impartial judge. "
            "Evaluate the following response based on the prompt provided. "
            "Respond with a score from 0.0 to 1.0, where 1.0 means 'definitely yes', "
            "and 0.0 means 'definitely no'. "
            "Also provide a confidence level from 0.0 to 1.0 "
            "indicating how sure you are about your score, and give brief feedback.\n\n"
            f"Prompt: {prompt}\n\n"
            "Format your answer as follows:\n"
            "Score: <score>\n"
            "Confidence: <confidence>\n"
            "Feedback: <feedback>"
        )

        output = self.client.chat(
            model=JUDGE_MODEL,
            messages=[
                Message(role="system", content=full_prompt),
                Message(role="user", content=response),
            ],
            format=judgement_result_schema,
        )
        output_content = output.message.content
        assert output_content is not None, "Ollama response content is None"
        result_dict = json.loads(output_content)
        score = float(result_dict["score"])
        confidence = float(result_dict["confidence"])
        feedback = str(result_dict["feedback"])

        return JudgementResult(score=score, confidence=confidence, feedback=feedback)


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
