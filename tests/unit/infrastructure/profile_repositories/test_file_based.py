"""Test suite for profile repository."""

from unittest.mock import MagicMock

import pytest

from shtym.domain.profile import DEFAULT_PROFILE_NAME, Profile, ProfileNotFoundError
from shtym.infrastructure.fileio import FileReader, FileReadError
from shtym.infrastructure.llm_profile import LLMProfile
from shtym.infrastructure.profile_parsers import ProfileParserError, TOMLProfileParser
from shtym.infrastructure.profile_repositories import (
    FileBasedProfileRepository,
)


def test_get_nonexistent_profile_raises_error() -> None:
    """Test that getting a non-existent profile raises ProfileNotFoundError."""
    mock_file_reader = MagicMock(spec=FileReader)
    mock_file_reader.read_str.side_effect = FileReadError("File not found")
    mock_parser = MagicMock(spec=TOMLProfileParser)

    repository = FileBasedProfileRepository(
        file_reader=mock_file_reader, parser=mock_parser
    )

    with pytest.raises(ProfileNotFoundError) as exc_info:
        repository.get("nonexistent")

    assert exc_info.value.profile_name == "nonexistent"


def test_get_profile_from_parsed_content() -> None:
    """Test loading a custom profile from parsed content."""
    mock_file_reader = MagicMock(spec=FileReader)
    mock_file_reader.read_str.return_value = "dummy content"

    mock_profile = MagicMock(spec=Profile)
    mock_parser = MagicMock(spec=TOMLProfileParser)
    mock_parser.parse.return_value = {"summary": mock_profile}

    repository = FileBasedProfileRepository(
        file_reader=mock_file_reader, parser=mock_parser
    )
    profile = repository.get("summary")

    assert profile == mock_profile
    mock_file_reader.read_str.assert_called_once_with(encoding="utf-8")
    mock_parser.parse.assert_called_once_with("dummy content")


def test_get_profile_with_multiple_parsed_profiles() -> None:
    """Test loading specific profile when multiple profiles are parsed."""
    mock_file_reader = MagicMock(spec=FileReader)
    mock_file_reader.read_str.return_value = "dummy content"

    mock_summary_profile = MagicMock(spec=Profile)
    mock_translate_profile = MagicMock(spec=Profile)
    mock_parser = MagicMock(spec=TOMLProfileParser)
    mock_parser.parse.return_value = {
        "summary": mock_summary_profile,
        "translate": mock_translate_profile,
    }

    repository = FileBasedProfileRepository(
        file_reader=mock_file_reader, parser=mock_parser
    )

    # Get summary profile
    summary = repository.get("summary")
    assert summary == mock_summary_profile

    # Get translate profile
    translate = repository.get("translate")
    assert translate == mock_translate_profile


def test_get_nonexistent_profile_from_parsed_content_raises_error() -> None:
    """Test that requesting non-existent profile from parsed content raises error."""
    mock_file_reader = MagicMock(spec=FileReader)
    mock_file_reader.read_str.return_value = "dummy content"

    mock_profile = MagicMock(spec=Profile)
    mock_parser = MagicMock(spec=TOMLProfileParser)
    mock_parser.parse.return_value = {"summary": mock_profile}

    repository = FileBasedProfileRepository(
        file_reader=mock_file_reader, parser=mock_parser
    )

    with pytest.raises(ProfileNotFoundError) as exc_info:
        repository.get("nonexistent")

    assert exc_info.value.profile_name == "nonexistent"


def test_get_profile_when_file_read_fails() -> None:
    """Test that file read failure silently falls back to default (ADR-0011)."""
    mock_file_reader = MagicMock(spec=FileReader)
    mock_file_reader.read_str.side_effect = FileReadError("File not found")
    mock_parser = MagicMock(spec=TOMLProfileParser)

    repository = FileBasedProfileRepository(
        file_reader=mock_file_reader, parser=mock_parser
    )

    # Default profile should still work
    default = repository.get(DEFAULT_PROFILE_NAME)
    assert isinstance(default, LLMProfile)

    # Non-default profile should raise error
    with pytest.raises(ProfileNotFoundError):
        repository.get("summary")


def test_profiles_are_cached() -> None:
    """Test that profiles property caches results and doesn't re-read file."""
    mock_file_reader = MagicMock(spec=FileReader)
    mock_file_reader.read_str.return_value = "dummy content"

    mock_profile = MagicMock(spec=Profile)
    mock_parser = MagicMock(spec=TOMLProfileParser)
    mock_parser.parse.return_value = {"summary": mock_profile}

    repository = FileBasedProfileRepository(
        file_reader=mock_file_reader, parser=mock_parser
    )

    # First access
    profile1 = repository.get("summary")
    # Second access
    profile2 = repository.get("summary")

    assert profile1 == profile2
    # Should only read file once due to caching
    mock_file_reader.read_str.assert_called_once()
    mock_parser.parse.assert_called_once()


def test_get_profile_when_file_read_error_occurs() -> None:
    """Test that FileReadError during file read silently falls back (ADR-0011)."""
    mock_file_reader = MagicMock(spec=FileReader)
    mock_file_reader.read_str.side_effect = FileReadError("Permission denied")
    mock_parser = MagicMock(spec=TOMLProfileParser)

    repository = FileBasedProfileRepository(
        file_reader=mock_file_reader, parser=mock_parser
    )

    # Default profile should still work (silent fallback per ADR-0011)
    default = repository.get(DEFAULT_PROFILE_NAME)
    assert isinstance(default, LLMProfile)

    # Non-default profile should raise ProfileNotFoundError
    with pytest.raises(ProfileNotFoundError):
        repository.get("summary")


def test_get_profile_when_parser_raises_error() -> None:
    """Test that parser error silently falls back to default profile (ADR-0011)."""
    mock_file_reader = MagicMock(spec=FileReader)
    mock_file_reader.read_str.return_value = "invalid toml content"
    mock_parser = MagicMock(spec=TOMLProfileParser)
    mock_parser.parse.side_effect = ProfileParserError("Invalid TOML")

    repository = FileBasedProfileRepository(
        file_reader=mock_file_reader, parser=mock_parser
    )

    # Parser error should be caught and fall back to default profile (ADR-0011)
    profile = repository.get(DEFAULT_PROFILE_NAME)
    assert isinstance(profile, LLMProfile)

    # Non-default profile should raise ProfileNotFoundError (not ProfileParserError)
    with pytest.raises(ProfileNotFoundError):
        repository.get("summary")
