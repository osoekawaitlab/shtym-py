"""Test suite for file I/O utilities."""

from pathlib import Path

import pytest

from shtym.infrastructure.fileio import FileReader, FileReadError


def test_read_str_reads_file_content(tmp_path: Path) -> None:
    """Test that read_str successfully reads file content."""
    test_file = tmp_path / "test.txt"
    expected_content = "Hello, World!\nThis is a test."
    test_file.write_text(expected_content, encoding="utf-8")

    reader = FileReader(test_file)
    actual_content = reader.read_str(encoding="utf-8")

    assert actual_content == expected_content


def test_read_str_with_different_encoding(tmp_path: Path) -> None:
    """Test that read_str respects the specified encoding."""
    test_file = tmp_path / "test_encoding.txt"
    # Japanese text with UTF-8 encoding
    expected_content = "こんにちは、世界!"
    test_file.write_text(expected_content, encoding="utf-8")

    reader = FileReader(test_file)
    actual_content = reader.read_str(encoding="utf-8")

    assert actual_content == expected_content


def test_read_str_raises_error_when_file_not_found(tmp_path: Path) -> None:
    """Test that read_str raises FileReadError for nonexistent file."""
    nonexistent_file = tmp_path / "nonexistent.txt"

    reader = FileReader(nonexistent_file)

    with pytest.raises(FileReadError) as exc_info:
        reader.read_str(encoding="utf-8")

    assert "File not found" in str(exc_info.value)


def test_read_str_handles_empty_file(tmp_path: Path) -> None:
    """Test that read_str handles empty files correctly."""
    empty_file = tmp_path / "empty.txt"
    empty_file.write_text("", encoding="utf-8")

    reader = FileReader(empty_file)
    actual_content = reader.read_str(encoding="utf-8")

    assert actual_content == ""


def test_file_reader_stores_file_path(tmp_path: Path) -> None:
    """Test that FileReader stores the provided file path."""
    test_file = tmp_path / "test.txt"

    reader = FileReader(test_file)

    assert reader.file_path == test_file
