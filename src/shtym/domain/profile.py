"""Profile domain objects and abstractions."""

DEFAULT_PROFILE_NAME = "default"


class ProfileNotFoundError(Exception):
    """Raised when a profile is not found."""

    def __init__(self, profile_name: str) -> None:
        """Initialize the error.

        Args:
            profile_name: Name of the profile that was not found.
        """
        self.profile_name = profile_name
        super().__init__(f"Profile '{profile_name}' not found")


class Profile:
    """Domain object representing an output transformation profile."""


class ProfileRepository:
    """Repository for profiles."""

    def get(self, name: str) -> Profile:
        """Get a profile by name.

        Args:
            name: Profile name.

        Returns:
            Profile instance.

        Raises:
            ProfileNotFoundError: If profile is not found.
        """
        # For now, only default profile exists
        if name == DEFAULT_PROFILE_NAME:
            return Profile()
        raise ProfileNotFoundError(name)
