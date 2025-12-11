"""E2E test configuration and fixtures."""

import os
from pathlib import Path

import pytest
from pytest_httpserver import HTTPServer

# Skip entire module if ollama package is not installed (optional dependency)
pytest.importorskip(
    "ollama",
    reason=(
        "ollama package not installed; run 'pip install \"shtym[ollama]\"' "
        "to enable Ollama E2E tests."
    ),
)

# Import after importorskip to avoid import errors
from ollama import Client

from tests.e2e.helpers import (
    JUDGE_MODEL,
    OllamaJudge,
    OllamaRecorder,
    is_valid_recorder_mode,
)


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


@pytest.fixture
def ollama_recorder(
    httpserver: HTTPServer, request: pytest.FixtureRequest
) -> OllamaRecorder:
    """Create OllamaRecorder for recording/replaying Ollama API interactions.

    Usage in tests:
        def test_something(ollama_recorder):
            env = {"SHTYM_LLM_SETTINGS__BASE_URL": ollama_recorder.base_url}
            subprocess.run(["stym", "run", "echo", "test"], env=env)

    By default, uses replay mode with cassette at:
        tests/fixtures/cassettes/<test_module>/<test_name>.json

    To record new cassettes, set SHTYMTEST_RECORDER_MODE=record or auto.

    Args:
        httpserver: pytest-httpserver fixture
        request: pytest request object for test metadata

    Returns:
        OllamaRecorder instance
    """
    # Determine cassette path from test name
    test_module = Path(str(request.path)).stem  # e.g., "test_ollama_integration"
    test_name = request.node.name  # e.g., "test_basic_functionality"
    cassette_dir = Path(__file__).parent.parent / "fixtures" / "cassettes" / test_module
    cassette_path = cassette_dir / f"{test_name}.json"

    # Get recording mode from environment
    mode = os.getenv("SHTYMTEST_RECORDER_MODE", "replay")
    if not is_valid_recorder_mode(mode):
        msg = (
            "Invalid SHTYMTEST_RECORDER_MODE: "
            f"{mode}. Must be 'record', 'replay', or 'auto'."
        )
        raise ValueError(msg)

    # Get real Ollama URL
    real_base_url = os.getenv("SHTYM_LLM_SETTINGS__BASE_URL", "http://localhost:11434")

    return OllamaRecorder(
        httpserver=httpserver,
        cassette_path=cassette_path,
        mode=mode,
        real_base_url=real_base_url,
    )
