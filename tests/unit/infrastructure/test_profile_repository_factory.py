"""Tests for ProfileRepositoryFactory."""

from pathlib import Path
from unittest.mock import call

from pytest_mock import MockerFixture

from shtym.infrastructure.profile_repository_factory import (
    ProfileRepositoryFactory,
)


def test_profile_repository_factory_implements_create_method(
    mocker: MockerFixture,
) -> None:
    """Test that ProfileRepositoryFactory has a create method."""
    file_reader = mocker.patch(
        "shtym.infrastructure.profile_repository_factory.FileReader"
    )
    toml_profile_parser = mocker.patch(
        "shtym.infrastructure.profile_repository_factory.TOMLProfileParser"
    )
    multi_source_profile_registry = mocker.patch(
        "shtym.infrastructure.profile_repository_factory.MultiSourceProfileRepository"
    )
    file_based_profile_registry = mocker.patch(
        "shtym.infrastructure.profile_repository_factory.FileBasedProfileRepository"
    )
    builtin_default_profile_registry = mocker.patch(
        "shtym.infrastructure.profile_repository_factory.BuiltinDefaultProfileRepository"
    )
    expected = multi_source_profile_registry.return_value
    actual = ProfileRepositoryFactory.create()

    assert actual == expected
    multi_source_profile_registry.assert_called_once_with(
        repositories=[
            file_based_profile_registry.return_value,
            file_based_profile_registry.return_value,
            builtin_default_profile_registry.return_value,
        ],
    )
    file_based_profile_registry.assert_has_calls(
        [
            call(
                file_reader=file_reader.return_value,
                parser=toml_profile_parser.return_value,
            ),
            call(
                file_reader=file_reader.return_value,
                parser=toml_profile_parser.return_value,
            ),
        ]
    )
    builtin_default_profile_registry.assert_called_once_with()
    file_reader.assert_has_calls(
        [
            call(file_path=Path(".shtym") / "profiles.toml"),
            call(file_path=Path.home() / ".config" / "shtym" / "profiles.toml"),
        ]
    )
    toml_profile_parser.assert_called_once_with()
