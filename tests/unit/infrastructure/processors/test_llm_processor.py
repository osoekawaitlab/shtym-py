"""Test suite for LLM processor implementation."""

import pytest
from pytest_mock import MockerFixture

from shtym.infrastructure.llm_profile import LLMProfile

try:
    from shtym.domain.processor import CommandExecution
    from shtym.infrastructure.processors.llm_processor import LLMProcessor

    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False


@pytest.mark.skipif(not OLLAMA_AVAILABLE, reason="ollama not installed")
def test_llm_processor_returns_processed_text_on_success(mocker: MockerFixture) -> None:
    """Test that LLMProcessor returns processed text when LLM responds successfully."""
    llm_client = mocker.Mock()
    llm_client.chat.return_value = "summary"
    prompt_template = (
        "Your task is to summarize and distill the essential information"
        " from the command $command:\n\n"
        "The provided user message is the raw output of the command so it may"
        " contain extraneous information, errors, or formatting artifacts."
        " Your goal is to extract the most relevant and accurate information."
        " Also, error will be provided if any as a separate user message."
    )
    sut = LLMProcessor(llm_client=llm_client, prompt_template=prompt_template)
    execution = CommandExecution(
        command=["echo", "test"], stdout="test output", stderr=""
    )

    result = sut.process(execution)

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
    prompt_template = "Summarize command $command"
    sut = LLMProcessor(llm_client=llm_client, prompt_template=prompt_template)
    execution = CommandExecution(
        command=["echo", "test"], stdout="test output", stderr=""
    )

    result = sut.process(execution)

    assert result == "test output"
    llm_client.chat.assert_called_once()


@pytest.mark.skipif(not OLLAMA_AVAILABLE, reason="ollama not installed")
def test_llm_processor_falls_back_on_any_error(mocker: MockerFixture) -> None:
    """Test that LLMProcessor falls back to raw output on any exception."""
    llm_client = mocker.Mock()
    llm_client.chat.side_effect = RuntimeError("Unexpected error")
    prompt_template = "Summarize command $command"
    sut = LLMProcessor(llm_client=llm_client, prompt_template=prompt_template)
    execution = CommandExecution(
        command=["echo", "test"], stdout="test output", stderr=""
    )

    result = sut.process(execution)

    assert result == "test output"
    llm_client.chat.assert_called_once()


def test_llm_processor_create_deligates_to_llm_client_factory(
    mocker: MockerFixture,
) -> None:
    """Test that LLMProcessor.create delegates to LLMClientFactory."""
    profile = LLMProfile()
    llm_client_factory_mock = mocker.patch(
        "shtym.infrastructure.processors.llm_processor.LLMClientFactory"
    )

    actual = LLMProcessor.create(profile=profile)

    llm_client_factory_mock.return_value.create.assert_called_once_with(
        profile=profile.llm_settings
    )
    assert actual.prompt_template == profile.prompt_template
    assert actual.llm_client == llm_client_factory_mock.return_value.create.return_value
