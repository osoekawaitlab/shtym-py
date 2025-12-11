"""Helpers for end-to-end tests."""

import hashlib
import json
import re
import urllib.parse
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, TypedDict, TypeGuard, cast

import httpx
import pytest
from pytest_httpserver import HTTPServer
from pytest_httpserver.httpserver import HandlerType
from werkzeug.wrappers import Request, Response

# Skip entire module if ollama package is not installed (optional dependency)
pytest.importorskip(
    "ollama",
    reason=(
        "ollama package not installed; run 'pip install \"shtym[ollama]\"' "
        "to enable Ollama E2E tests."
    ),
)

from ollama import Client, Message

RecorderMode = Literal["record", "replay", "auto"]


def is_valid_recorder_mode(mode: str) -> TypeGuard[RecorderMode]:
    """Check if the given mode is a valid RecorderMode."""
    return mode in {"record", "replay", "auto"}


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


class CassetteRequest(TypedDict):
    """Recorded request for cassette storage."""

    method: str
    path: str
    query: str
    body: str
    headers: dict[str, str]


class CassetteResponse(TypedDict):
    """Recorded response for cassette storage."""

    status: int
    body: str
    headers: dict[str, str]


class CassetteRecord(TypedDict):
    """Cassette entry keyed by normalized request."""

    request: CassetteRequest
    response: CassetteResponse


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


class OllamaRecorder:
    """HTTP recorder for Ollama API interactions.

    Records HTTP requests/responses to cassette files for replay in tests.
    This allows E2E tests to run without a real Ollama server.
    """

    def __init__(
        self,
        httpserver: HTTPServer,
        cassette_path: Path,
        mode: RecorderMode = "replay",
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
        self._cassette_data: dict[str, CassetteRecord] = {}

        if mode in {"replay", "auto"}:
            self._load_cassette()

        # Register a permanent handler for all Ollama API endpoints.
        pattern = re.compile(r"/api/.*")
        self.httpserver.expect_request(
            pattern, handler_type=HandlerType.PERMANENT
        ).respond_with_handler(self._handle_request)

    def get_recorded_requests(self) -> dict[str, CassetteRecord]:
        """Get all recorded requests and responses.

        Returns:
            Dictionary mapping request hashes to request/response data
        """
        return self._cassette_data.copy()

    def _load_cassette(self) -> None:
        """Load cassette from file if it exists."""
        if self.cassette_path.exists():
            with self.cassette_path.open() as f:
                loaded = json.load(f)
                self._cassette_data = cast("dict[str, CassetteRecord]", loaded)

    def _save_cassette(self) -> None:
        """Save cassette to file."""
        self.cassette_path.parent.mkdir(parents=True, exist_ok=True)
        with self.cassette_path.open("w") as f:
            json.dump(self._cassette_data, f, indent=2)

    def _make_key(self, request: Request) -> str:
        """Generate unique key for request based on method, path/query, and body."""
        normalized_body = self._normalize_body(request.get_data())
        canonical_path = self._canonicalize_path(request)
        normalized_headers = self._normalize_headers_for_key(dict(request.headers))
        key_data = (
            f"{request.method}:{canonical_path}:{normalized_body}:{normalized_headers}"
        )
        return hashlib.sha256(key_data.encode()).hexdigest()

    def _canonicalize_path(self, request: Request) -> str:
        """Normalize query strings so parameter order does not change the key."""
        if not request.query_string:
            return request.path
        query_pairs = urllib.parse.parse_qsl(
            request.query_string.decode(errors="replace"), keep_blank_values=True
        )
        canonical_query = urllib.parse.urlencode(sorted(query_pairs))
        return f"{request.path}?{canonical_query}"

    def _normalize_body(self, body: bytes) -> str:
        """Normalize request body to make cassette keys stable."""
        if not body:
            return ""

        try:
            text = body.decode()
        except UnicodeDecodeError:
            return hashlib.sha256(body).hexdigest()

        try:
            parsed = json.loads(text)
        except ValueError:
            return text

        return json.dumps(parsed, sort_keys=True, separators=(",", ":"))

    def _normalize_headers_for_key(self, headers: Mapping[str, str]) -> str:
        """Normalize whitelisted headers for stable cassette keys."""
        filtered = self._filter_request_headers(dict(headers))
        if not filtered:
            return ""
        return json.dumps(filtered, sort_keys=True, separators=(",", ":"))

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
                "query": request.query_string.decode(errors="replace"),
                "body": request.get_data(as_text=True),
                "headers": self._filter_request_headers(dict(request.headers)),
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
        url = self._build_target_url(request)

        # Use extended timeout for LLM requests (can take a long time)
        timeout = httpx.Timeout(300.0, connect=10.0)  # 5 minutes for read

        with httpx.Client(timeout=timeout) as client:
            return client.request(
                method=request.method,
                url=url,
                content=request.get_data(),
                headers=self._prepare_forward_headers(dict(request.headers)),
            )

    @property
    def base_url(self) -> str:
        """Get the base URL of the recording proxy server.

        Returns:
            URL to use for SHTYM_LLM_SETTINGS__BASE_URL
        """
        url: str = self.httpserver.url_for("/")
        return url

    def _build_target_url(self, request: Request) -> str:
        """Build URL for the real server including query parameters."""
        if request.query_string:
            query = request.query_string.decode(errors="replace")
            return f"{self.real_base_url}{request.path}?{query}"
        return f"{self.real_base_url}{request.path}"

    def _prepare_forward_headers(self, headers: dict[str, str]) -> dict[str, str]:
        """Drop headers that should be regenerated when proxying to the real server."""
        return {
            k: v
            for k, v in headers.items()
            if k.lower() not in {"host", "content-length"}
        }

    def _filter_request_headers(self, headers: dict[str, str]) -> dict[str, str]:
        """Keep only whitelisted headers for cassette logging."""
        allowed = {"content-type", "accept"}
        return {k: v for k, v in headers.items() if k.lower() in allowed}
