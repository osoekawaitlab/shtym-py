"""Test suite for filter domain logic."""

from pytest_mock import MockerFixture

from shtym.domain import filter as filter_module


def test_passthrough_filter_returns_input_unchanged() -> None:
    """Test that PassThroughFilter returns input text unchanged."""
    sut = filter_module.PassThroughFilter()

    result = sut.filter([], "test input text\n", "")

    assert result == "test input text\n"


def test_passthrough_filter_handles_empty_string() -> None:
    """Test that PassThroughFilter handles empty string."""
    sut = filter_module.PassThroughFilter()

    result = sut.filter([], "", "")

    assert result == ""


def test_passthrough_filter_handles_multiline() -> None:
    """Test that PassThroughFilter handles multiline text."""
    sut = filter_module.PassThroughFilter()
    input_text = "line 1\nline 2\nline 3\n"

    result = sut.filter([], input_text, "")

    assert result == input_text


def test_llm_filter_returns_filtered_text_on_success(mocker: MockerFixture) -> None:
    """Test that LLMFilter returns filtered text when LLM responds successfully."""
    llm_client = mocker.Mock()
    llm_client.chat.return_value = "summary"
    sut = filter_module.LLMFilter(llm_client=llm_client)

    result = sut.filter(command=["echo", "test"], stdout="test output", stderr="")

    llm_client.chat.assert_called_once()
    call_args = llm_client.chat.call_args
    assert "echo test" in call_args.kwargs["system_prompt"]
    assert call_args.kwargs["user_prompt"] == "test output"
    assert call_args.kwargs["error_message"] == ""
    assert result == "summary"
