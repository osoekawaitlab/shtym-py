"""Test suite for processor domain logic."""

import pytest
from pytest_mock import MockerFixture

from shtym.domain import processor as processor_module

try:
    from shtym.domain.processor import LLMProcessor  # noqa: F401

    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False


def test_passthrough_processor_returns_input_unchanged() -> None:
    """Test that PassThroughProcessor returns input text unchanged."""
    sut = processor_module.PassThroughProcessor()

    result = sut.process([], "test input text\n", "")

    assert result == "test input text\n"


def test_passthrough_processor_handles_empty_string() -> None:
    """Test that PassThroughProcessor handles empty string."""
    sut = processor_module.PassThroughProcessor()

    result = sut.process([], "", "")

    assert result == ""


def test_passthrough_processor_handles_multiline() -> None:
    """Test that PassThroughProcessor handles multiline text."""
    sut = processor_module.PassThroughProcessor()
    input_text = "line 1\nline 2\nline 3\n"

    result = sut.process([], input_text, "")

    assert result == input_text


@pytest.mark.skipif(not OLLAMA_AVAILABLE, reason="ollama not installed")
def test_llm_processor_returns_processed_text_on_success(mocker: MockerFixture) -> None:
    """Test that LLMProcessor returns processed text when LLM responds successfully."""
    llm_client = mocker.Mock()
    llm_client.chat.return_value = "summary"
    sut = processor_module.LLMProcessor(llm_client=llm_client)

    result = sut.process(command=["echo", "test"], stdout="test output", stderr="")

    llm_client.chat.assert_called_once()
    call_args = llm_client.chat.call_args
    assert "echo test" in call_args.kwargs["system_prompt"]
    assert call_args.kwargs["user_prompt"] == "test output"
    assert call_args.kwargs["error_message"] == ""
    assert result == "summary"


@pytest.mark.skipif(not OLLAMA_AVAILABLE, reason="ollama not installed")
def test_llm_processor_falls_back_on_connection_error(mocker: MockerFixture) -> None:
    """Test that LLMProcessor falls back to raw output when LLM connection fails."""
    llm_client = mocker.Mock()
    llm_client.chat.side_effect = ConnectionError("Ollama not reachable")
    sut = processor_module.LLMProcessor(llm_client=llm_client)

    result = sut.process(command=["echo", "test"], stdout="test output", stderr="")

    assert result == "test output"
    llm_client.chat.assert_called_once()


@pytest.mark.skipif(not OLLAMA_AVAILABLE, reason="ollama not installed")
def test_llm_processor_falls_back_on_any_error(mocker: MockerFixture) -> None:
    """Test that LLMProcessor falls back to raw output on any exception."""
    llm_client = mocker.Mock()
    llm_client.chat.side_effect = RuntimeError("Unexpected error")
    sut = processor_module.LLMProcessor(llm_client=llm_client)

    result = sut.process(command=["echo", "test"], stdout="test output", stderr="")

    assert result == "test output"
    llm_client.chat.assert_called_once()
