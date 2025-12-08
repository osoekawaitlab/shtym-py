"""E2E test configuration and fixtures."""

import os

import pytest

# Skip entire module if ollama package is not installed (optional dependency)
pytest.importorskip(
    "ollama",
    reason=(
        "ollama package not installed; run 'pip install \"shtym[ollama]\"' "
        "to enable Ollama E2E tests."
    ),
)

# Import after importorskip to avoid import errors
import ollama

from tests.e2e.test_ollama_judge import JUDGE_MODEL, OllamaJudge

Client = ollama.Client


@pytest.fixture(scope="session")
def ollama_environment() -> str:
    """Check Ollama environment setup once per test session.

    Uses SHTYM_LLM_SETTINGS__BASE_URL if set, otherwise defaults to
    http://localhost:11434. Fails if Ollama is not available at the URL.
    This ensures E2E test environment is properly configured.

    Returns:
        Base URL of the Ollama service.

    Raises:
        pytest.fail: If Ollama is not available at the configured URL.
    """
    base_url = os.getenv("SHTYM_LLM_SETTINGS__BASE_URL", "http://localhost:11434")

    # Check LLM connection (executed once per session)
    try:
        client = Client(host=base_url)
        client.list()
    except (ConnectionError, OSError) as e:
        pytest.fail(
            f"Ollama not available at {base_url}: {e}. "
            "E2E test environment is not properly configured."
        )

    return base_url


@pytest.fixture(scope="session")
def ollama_judge(ollama_environment: str) -> OllamaJudge:
    """Create OllamaJudge once per session.

    Requires SHTYMTEST_ENABLE_LLM_JUDGE environment variable to be set.
    This allows skipping expensive LLM-as-a-Judge tests in CI/CD environments.

    Args:
        ollama_environment: Base URL from ollama_environment fixture.

    Returns:
        OllamaJudge instance for testing.

    Raises:
        pytest.skip: If SHTYMTEST_ENABLE_LLM_JUDGE is not set.
        pytest.fail: If judge model is not available.
    """
    if not os.getenv("SHTYMTEST_ENABLE_LLM_JUDGE"):
        pytest.skip("SHTYMTEST_ENABLE_LLM_JUDGE not set; skipping LLM-as-a-Judge tests")

    try:
        judge = OllamaJudge.create(base_url=ollama_environment)
    except AssertionError as e:
        pytest.fail(
            f"Judge model {JUDGE_MODEL} not available. "
            f"E2E test environment is not properly configured: {e}"
        )

    return judge
