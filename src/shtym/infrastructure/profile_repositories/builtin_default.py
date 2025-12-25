"""Profile repository with built-in default profiles."""

from shtym.domain.profile import Profile, ProfileNotFoundError
from shtym.infrastructure.llm_profile import LLMProfile


class BuiltinDefaultProfileRepository:
    """Profile repository that provides built-in default profiles."""

    def get(self, name: str) -> Profile:
        """Get a profile by name.

        Args:
            name: Profile name.

        Returns:
            Profile instance.

        Raises:
            ProfileNotFoundError: If profile is not found.
        """
        if name == "default":
            # Return a built-in default profile instance
            return LLMProfile()  # Replace with actual default profile implementation

        raise ProfileNotFoundError(name)
