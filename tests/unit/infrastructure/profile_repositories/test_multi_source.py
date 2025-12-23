"""MultiSourceProfileRepository tests."""

from unittest.mock import MagicMock

import pytest

from shtym.domain.profile import Profile, ProfileNotFoundError
from shtym.infrastructure.profile_repositories import (
    FileBasedProfileRepository,
    MultiSourceProfileRepository,
)


def test_raises_error_when_profile_not_found() -> None:
    """Test that ProfileNotFoundError is raised when profile is not found."""
    # Setup two repositories that do not have the profile
    first_repo = MagicMock(spec=FileBasedProfileRepository)
    first_repo.get.side_effect = ProfileNotFoundError("test-profile")

    second_repo = MagicMock(spec=FileBasedProfileRepository)
    second_repo.get.side_effect = ProfileNotFoundError("test-profile")

    multi_repo = MultiSourceProfileRepository(repositories=[first_repo, second_repo])

    with pytest.raises(ProfileNotFoundError) as exc_info:
        multi_repo.get("test-profile")

    assert exc_info.value.profile_name == "test-profile"
    first_repo.get.assert_called_once_with("test-profile")
    second_repo.get.assert_called_once_with("test-profile")


def test_returns_profile_from_first_repository() -> None:
    """Test that profile is returned from the first repository that has it."""
    # Setup first repository with the profile
    first_profile = MagicMock(spec=Profile)
    first_repo = MagicMock(spec=FileBasedProfileRepository)
    first_repo.get.return_value = first_profile

    # Setup second repository (shouldn't be called)
    second_repo = MagicMock(spec=FileBasedProfileRepository)

    multi_repo = MultiSourceProfileRepository(repositories=[first_repo, second_repo])

    result = multi_repo.get("test-profile")

    # Should return from first repository
    assert result == first_profile
    first_repo.get.assert_called_once_with("test-profile")
    # Second repository should not be called
    second_repo.get.assert_not_called()
