"""Test suite for filter domain logic."""

from shtym.domain import filter as filter_module


def test_passthrough_filter_returns_input_unchanged() -> None:
    """Test that PassThroughFilter returns input text unchanged."""
    sut = filter_module.PassThroughFilter()

    result = sut.filter("test input text\n")

    assert result == "test input text\n"


def test_passthrough_filter_handles_empty_string() -> None:
    """Test that PassThroughFilter handles empty string."""
    sut = filter_module.PassThroughFilter()

    result = sut.filter("")

    assert result == ""


def test_passthrough_filter_handles_multiline() -> None:
    """Test that PassThroughFilter handles multiline text."""
    sut = filter_module.PassThroughFilter()
    input_text = "line 1\nline 2\nline 3\n"

    result = sut.filter(input_text)

    assert result == input_text
