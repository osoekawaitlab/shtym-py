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
    system_prompt_template = (
        "Your task is to summarize and distill the essential information "
        "from the command $command."
    )
    user_prompt_template = "Output:\n$stdout\n\nErrors:\n$stderr"
    sut = LLMProcessor(
        llm_client=llm_client,
        system_prompt_template=system_prompt_template,
        user_prompt_template=user_prompt_template,
    )
    execution = CommandExecution(
        command=["echo", "test"], stdout="test output", stderr=""
    )

    result = sut.process(execution)

    llm_client.chat.assert_called_once()
    call_args = llm_client.chat.call_args
    assert "echo test" in call_args.kwargs["system_prompt"]
    assert "test output" in call_args.kwargs["user_prompt"]
    assert call_args.kwargs["error_message"] == ""
    assert result == "summary"


@pytest.mark.skipif(not OLLAMA_AVAILABLE, reason="ollama not installed")
def test_llm_processor_falls_back_on_connection_error(mocker: MockerFixture) -> None:
    """Test that LLMProcessor falls back to raw output when LLM connection fails."""
    llm_client = mocker.Mock()
    llm_client.chat.side_effect = ConnectionError("Ollama not reachable")
    system_prompt_template = "Summarize command $command"
    user_prompt_template = "$stdout"
    sut = LLMProcessor(
        llm_client=llm_client,
        system_prompt_template=system_prompt_template,
        user_prompt_template=user_prompt_template,
    )
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
    system_prompt_template = "Summarize command $command"
    user_prompt_template = "$stdout"
    sut = LLMProcessor(
        llm_client=llm_client,
        system_prompt_template=system_prompt_template,
        user_prompt_template=user_prompt_template,
    )
    execution = CommandExecution(
        command=["echo", "test"], stdout="test output", stderr=""
    )

    result = sut.process(execution)

    assert result == "test output"
    llm_client.chat.assert_called_once()


def test_llm_processor_create_delegates_to_llm_client_factory(
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
    assert actual.system_prompt_template == profile.system_prompt_template
    assert actual.user_prompt_template == profile.user_prompt_template
    assert actual.llm_client == llm_client_factory_mock.return_value.create.return_value


@pytest.mark.skipif(not OLLAMA_AVAILABLE, reason="ollama not installed")
def test_llm_processor_can_use_stdout_in_system_prompt(mocker: MockerFixture) -> None:
    """Test that system_prompt_template can use $stdout variable.

    This verifies that both templates have access to all template variables
    (command, stdout, stderr) for maximum flexibility.
    """
    llm_client = mocker.Mock()
    llm_client.chat.return_value = "processed"
    # Use $stdout in system prompt template (should not raise KeyError)
    system_prompt_template = "Context: $stdout"
    user_prompt_template = "Command was: $command"
    sut = LLMProcessor(
        llm_client=llm_client,
        system_prompt_template=system_prompt_template,
        user_prompt_template=user_prompt_template,
    )
    execution = CommandExecution(
        command=["echo", "test"], stdout="test output", stderr=""
    )

    result = sut.process(execution)

    llm_client.chat.assert_called_once()
    call_args = llm_client.chat.call_args
    # Verify $stdout was substituted in system prompt
    assert call_args.kwargs["system_prompt"] == "Context: test output"
    # Verify $command was substituted in user prompt
    assert call_args.kwargs["user_prompt"] == "Command was: echo test"
    assert result == "processed"


@pytest.mark.skipif(not OLLAMA_AVAILABLE, reason="ollama not installed")
def test_llm_processor_all_variables_available_in_both_templates(
    mocker: MockerFixture,
) -> None:
    """Test that all template variables are available in both templates.

    This verifies that command, stdout, and stderr can all be used in
    both system_prompt_template and user_prompt_template.
    """
    llm_client = mocker.Mock()
    llm_client.chat.return_value = "result"
    # Use all variables in both templates
    system_prompt_template = "Cmd: $command, Out: $stdout, Err: $stderr"
    user_prompt_template = "Again - Cmd: $command, Out: $stdout, Err: $stderr"
    sut = LLMProcessor(
        llm_client=llm_client,
        system_prompt_template=system_prompt_template,
        user_prompt_template=user_prompt_template,
    )
    execution = CommandExecution(
        command=["ls", "-la"], stdout="file1\nfile2", stderr="warning"
    )

    result = sut.process(execution)

    llm_client.chat.assert_called_once()
    call_args = llm_client.chat.call_args
    expected_system = "Cmd: ls -la, Out: file1\nfile2, Err: warning"
    expected_user = "Again - Cmd: ls -la, Out: file1\nfile2, Err: warning"
    assert call_args.kwargs["system_prompt"] == expected_system
    assert call_args.kwargs["user_prompt"] == expected_user
    assert result == "result"
