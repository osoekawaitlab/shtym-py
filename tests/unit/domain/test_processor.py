"""Test suite for processor domain logic."""

from shtym.domain import processor as processor_module


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
