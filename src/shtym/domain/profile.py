"""Profile domain protocols and abstractions."""

from typing import Protocol

from shtym.exceptions import ShtymDomainError

DEFAULT_PROFILE_NAME = "default"


class ProfileNotFoundError(ShtymDomainError):
    """Raised when a profile is not found.

    This error indicates that the requested profile does not exist
    in the repository. The system should fall back to PassThroughProcessor.
    """

    def __init__(self, profile_name: str) -> None:
        """Initialize the error.

        Args:
            profile_name: Name of the profile that was not found.
        """
        self.profile_name = profile_name
        super().__init__(f"Profile '{profile_name}' not found")


class Profile(Protocol):
    """Protocol for output transformation profile.

    A profile represents a named configuration for how to transform command output.
    The profile itself is an abstract concept in the domain layer.
    Concrete implementations in the infrastructure layer contain specific settings.
    """


class ProfileRepository(Protocol):
    """Protocol for profile repository."""

    def get(self, name: str) -> Profile:
        """Get a profile by name.

        Args:
            name: Profile name.

        Returns:
            Profile instance.

        Raises:
            ProfileNotFoundError: If profile is not found.
        """
