"""E2E test configuration and fixtures."""

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any

import httpx
import pytest
from pytest_httpserver import HTTPServer
from werkzeug.wrappers import Request, Response

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


class OllamaRecorder:
    """HTTP recorder for Ollama API interactions.

    Records HTTP requests/responses to cassette files for replay in tests.
    This allows E2E tests to run without a real Ollama server.
    """

    def __init__(
        self,
        httpserver: HTTPServer,
        cassette_path: Path,
        mode: str = "replay",
        real_base_url: str = "http://localhost:11434",
    ) -> None:
        """Initialize the Ollama recorder.

        Args:
            httpserver: pytest-httpserver instance
            cassette_path: Path to cassette file for recording/replay
            mode: Recording mode - "record", "replay", or "auto"
            real_base_url: Real Ollama server URL for record mode
        """
        self.httpserver = httpserver
        self.cassette_path = cassette_path
        self.mode = mode
        self.real_base_url = real_base_url
        self._cassette_data: dict[str, Any] = {}

        if mode in {"replay", "auto"}:
            self._load_cassette()

        # Register permanent handler for all Ollama API endpoints
        # This will handle multiple requests without being consumed
        for _ in range(100):  # Register handler many times for multiple requests
            self.httpserver.expect_request(re.compile(r"/api/.*")).respond_with_handler(
                self._handle_request
            )

    def get_recorded_requests(self) -> dict[str, Any]:
        """Get all recorded requests and responses.

        Returns:
            Dictionary mapping request hashes to request/response data
        """
        return self._cassette_data.copy()

    def _load_cassette(self) -> None:
        """Load cassette from file if it exists."""
        if self.cassette_path.exists():
            with self.cassette_path.open() as f:
                self._cassette_data = json.load(f)

    def _save_cassette(self) -> None:
        """Save cassette to file."""
        self.cassette_path.parent.mkdir(parents=True, exist_ok=True)
        with self.cassette_path.open("w") as f:
            json.dump(self._cassette_data, f, indent=2)

    def _make_key(self, request: Request) -> str:
        """Generate unique key for request based on method, path, and body.

        Args:
            request: The HTTP request

        Returns:
            Hash string representing the request
        """
        body = request.get_data(as_text=True)
        key_data = f"{request.method}:{request.path}:{body}"
        return hashlib.sha256(key_data.encode()).hexdigest()

    def _filter_problematic_headers(self, headers: dict[str, str]) -> dict[str, str]:
        """Filter out headers that cause issues when replaying responses.

        Args:
            headers: Original headers dictionary

        Returns:
            Filtered headers dictionary without problematic headers
        """
        return {
            k: v
            for k, v in headers.items()
            if k.lower() not in {"transfer-encoding", "content-encoding"}
        }

    def _handle_request(self, request: Request) -> Response:
        """Handle incoming request - replay from cassette or forward to real server.

        Args:
            request: The HTTP request

        Returns:
            HTTP response from cassette or real server
        """
        key = self._make_key(request)

        # Try replay mode first
        if self.mode == "replay" or (
            self.mode == "auto" and key in self._cassette_data
        ):
            if key in self._cassette_data:
                recorded = self._cassette_data[key]
                headers = self._filter_problematic_headers(
                    recorded["response"]["headers"]
                )
                return Response(
                    response=recorded["response"]["body"],
                    status=recorded["response"]["status"],
                    headers=headers,
                )
            if self.mode == "replay":
                msg = (
                    f"No recorded response for request {request.method} "
                    f"{request.path}. Run test in 'record' or 'auto' mode "
                    "to record interactions."
                )
                raise KeyError(msg)

        # Record mode or auto mode without recording
        response = self._forward_to_real_server(request)

        # Save to cassette (filter problematic headers for storage)
        headers = self._filter_problematic_headers(dict(response.headers))

        self._cassette_data[key] = {
            "request": {
                "method": request.method,
                "path": request.path,
                "body": request.get_data(as_text=True),
                "headers": dict(request.headers),
            },
            "response": {
                "status": response.status_code,
                "body": response.text,
                "headers": headers,
            },
        }
        self._save_cassette()

        return Response(
            response=response.text,
            status=response.status_code,
            headers=headers,
        )

    def _forward_to_real_server(self, request: Request) -> httpx.Response:
        """Forward request to real Ollama server.

        Args:
            request: The HTTP request to forward

        Returns:
            Response from real server

        Raises:
            ConnectionError: If real server is not available
        """
        url = f"{self.real_base_url}{request.path}"

        # Use extended timeout for LLM requests (can take a long time)
        timeout = httpx.Timeout(300.0, connect=10.0)  # 5 minutes for read

        with httpx.Client(timeout=timeout) as client:
            return client.request(
                method=request.method,
                url=url,
                content=request.get_data(),
                headers=dict(request.headers),
            )

    @property
    def base_url(self) -> str:
        """Get the base URL of the recording proxy server.

        Returns:
            URL to use for SHTYM_LLM_SETTINGS__BASE_URL
        """
        url: str = self.httpserver.url_for("/")
        return url


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

    To record new cassettes, set SHTYM_RECORDER_MODE=record or auto.

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
    mode = os.getenv("SHTYM_RECORDER_MODE", "replay")

    # Get real Ollama URL
    real_base_url = os.getenv("SHTYM_LLM_SETTINGS__BASE_URL", "http://localhost:11434")

    return OllamaRecorder(
        httpserver=httpserver,
        cassette_path=cassette_path,
        mode=mode,
        real_base_url=real_base_url,
    )
