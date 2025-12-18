"""Test suite for profile parsers."""

import pytest

from shtym.infrastructure.llm_profile import LLMProfile
from shtym.infrastructure.profile_parsers import ProfileParserError, TOMLProfileParser


def test_parse_valid_toml_with_single_profile() -> None:
    """Test parsing valid TOML with a single profile."""
    toml_content = """
[profiles.summary]
type = "llm"
prompt_template = "Summarize: $command"

[profiles.summary.llm_settings]
model_name = "test-model"
base_url = "http://localhost:11434"
"""
    parser = TOMLProfileParser()
    profiles = parser.parse(toml_content)

    assert len(profiles) == 1
    assert "summary" in profiles
    assert isinstance(profiles["summary"], LLMProfile)
    assert profiles["summary"].prompt_template == "Summarize: $command"
    assert profiles["summary"].llm_settings.model_name == "test-model"
    assert str(profiles["summary"].llm_settings.base_url) == "http://localhost:11434/"


def test_parse_valid_toml_with_multiple_profiles() -> None:
    """Test parsing valid TOML with multiple profiles."""
    toml_content = """
[profiles.summary]
type = "llm"
prompt_template = "Summarize: $command"

[profiles.summary.llm_settings]
model_name = "summary-model"
base_url = "http://localhost:1111"

[profiles.translate]
type = "llm"
prompt_template = "Translate: $command"

[profiles.translate.llm_settings]
model_name = "translate-model"
base_url = "http://localhost:2222"
"""
    parser = TOMLProfileParser()
    profiles = parser.parse(toml_content)

    # Should parse exactly two profiles: summary and translate
    expected_profile_count = 2
    assert len(profiles) == expected_profile_count
    assert "summary" in profiles
    assert "translate" in profiles

    summary_profile = profiles["summary"]
    translate_profile = profiles["translate"]
    assert isinstance(summary_profile, LLMProfile)
    assert isinstance(translate_profile, LLMProfile)
    assert summary_profile.prompt_template == "Summarize: $command"
    assert translate_profile.prompt_template == "Translate: $command"


def test_parse_raises_error_on_invalid_toml_syntax() -> None:
    """Test that parser raises ProfileParserError on TOML syntax error."""
    invalid_toml = """
[profiles.summary
type = "llm"
"""
    parser = TOMLProfileParser()

    with pytest.raises(ProfileParserError) as exc_info:
        parser.parse(invalid_toml)

    assert "Profile parsing error" in str(exc_info.value)


def test_parse_raises_error_when_profiles_section_missing() -> None:
    """Test that parser raises ProfileParserError when 'profiles' section is missing."""
    toml_without_profiles = """
[other_section]
key = "value"
"""
    parser = TOMLProfileParser()

    with pytest.raises(ProfileParserError) as exc_info:
        parser.parse(toml_without_profiles)

    assert "Missing 'profiles' section" in str(exc_info.value)


def test_parse_raises_error_when_profiles_is_not_table() -> None:
    """Test that parser raises ProfileParserError when 'profiles' is not a table."""
    toml_with_invalid_profiles = """
profiles = "not a table"
"""
    parser = TOMLProfileParser()

    with pytest.raises(ProfileParserError) as exc_info:
        parser.parse(toml_with_invalid_profiles)

    assert "'profiles' section must be a table" in str(exc_info.value)


def test_parse_raises_error_on_validation_failure() -> None:
    """Test that parser raises ProfileParserError on Pydantic validation failure."""
    toml_with_invalid_data = """
[profiles.invalid]
type = "llm"
prompt_template = "Test: $command"

[profiles.invalid.llm_settings]
model_name = "test-model"
base_url = "not-a-valid-url"
"""
    parser = TOMLProfileParser()

    with pytest.raises(ProfileParserError) as exc_info:
        parser.parse(toml_with_invalid_data)

    assert "Invalid profile data" in str(exc_info.value)


def test_parse_profile_with_defaults() -> None:
    """Test parsing profile that relies on default values."""
    toml_content = """
[profiles.minimal]
type = "llm"
"""
    parser = TOMLProfileParser()
    profiles = parser.parse(toml_content)

    assert "minimal" in profiles
    assert isinstance(profiles["minimal"], LLMProfile)
    # Should use default prompt_template and llm_settings
    assert profiles["minimal"].prompt_template is not None
    assert profiles["minimal"].llm_settings is not None


def test_parse_empty_profiles_section() -> None:
    """Test parsing TOML with empty profiles section."""
    toml_content = """
[profiles]
"""
    parser = TOMLProfileParser()
    profiles = parser.parse(toml_content)

    assert len(profiles) == 0


def test_parse_raises_error_on_invalid_type() -> None:
    """Test that parser raises ProfileParserError for invalid type field."""
    toml_content = """
[profiles.invalid_type]
type = "unknown"
prompt_template = "Test: $command"
"""
    parser = TOMLProfileParser()

    with pytest.raises(ProfileParserError) as exc_info:
        parser.parse(toml_content)

    error_message = str(exc_info.value).lower()
    assert "invalid profile type" in error_message or "type" in error_message
