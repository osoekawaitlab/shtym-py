"""Profile repository implementation."""

from shtym.domain.profile import DEFAULT_PROFILE_NAME, Profile, ProfileNotFoundError
from shtym.infrastructure.llm_profile import LLMProfile


class FileBasedProfileRepository:
    """Profile repository that loads profiles from environment variables.

    Currently only supports the default profile loaded from environment variables.
    Future versions will support loading custom profiles from files.
    """

    def get(self, name: str) -> Profile:
        """Get a profile by name.

        Args:
            name: Profile name.

        Returns:
            Profile instance.

        Raises:
            ProfileNotFoundError: If profile is not found.
        """
        if name == DEFAULT_PROFILE_NAME:
            return LLMProfile()
        raise ProfileNotFoundError(name)
