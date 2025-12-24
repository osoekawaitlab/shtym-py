"""Multi-source profile repository implementation."""

from shtym.domain.profile import Profile, ProfileNotFoundError, ProfileRepository


class MultiSourceProfileRepository:
    """Profile repository that loads profiles from multiple sources with priority.

    Searches for profiles across multiple repositories in priority order.
    Returns the first matching profile found.
    """

    def __init__(self, repositories: list[ProfileRepository]) -> None:
        """Initialize the repository with a list of sources.

        Args:
            repositories: List of ProfileRepository instances, in priority order.
                         First repository has highest priority.
        """
        self.repositories = repositories

    def get(self, name: str) -> Profile:
        """Get a profile by name from the first repository that has it.

        Args:
            name: Profile name.

        Returns:
            Profile instance from the first repository that has it.

        Raises:
            ProfileNotFoundError: If profile is not found in any repository.
        """
        for repository in self.repositories:
            try:
                return repository.get(name)
            except ProfileNotFoundError:  # noqa: PERF203
                continue
        raise ProfileNotFoundError(name)
