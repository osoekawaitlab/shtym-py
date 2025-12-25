"""Profile repository implementation."""

from shtym.domain.profile import (
    Profile,
    ProfileNotFoundError,
)
from shtym.infrastructure.fileio import FileReader, FileReadError
from shtym.infrastructure.profile_parsers import ProfileParserError, TOMLProfileParser


class FileBasedProfileRepository:
    """Profile repository that loads profiles from configuration file.

    Loads profiles from a TOML file using FileReader and TOMLProfileParser.
    Always includes a default profile loaded from environment variables.
    """

    def __init__(self, file_reader: FileReader, parser: TOMLProfileParser) -> None:
        """Initialize the repository.

        Args:
            file_reader: FileReader instance for reading the profiles file.
            parser: TOMLProfileParser instance for parsing the file content.
        """
        self.file_reader = file_reader
        self.parser = parser
        self._profiles: dict[str, Profile] | None = None

    @property
    def profiles(self) -> dict[str, Profile]:
        """Get all available profiles.

        Returns:
            Dictionary of profile name to Profile instance.
        """
        if self._profiles is None:
            try:
                content = self.file_reader.read_str(encoding="utf-8")
                self._profiles = self.parser.parse(content)
            except (FileReadError, ProfileParserError):
                self._profiles = {}
        return self._profiles

    def get(self, name: str) -> Profile:
        """Get a profile by name.

        Args:
            name: Profile name.

        Returns:
            Profile instance.

        Raises:
            ProfileNotFoundError: If profile is not found.
        """
        if name in self.profiles:
            return self.profiles[name]
        raise ProfileNotFoundError(name)
