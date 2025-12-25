"""Profile repository factory."""

from pathlib import Path

from shtym.domain.profile import ProfileRepository
from shtym.infrastructure.fileio import FileReader
from shtym.infrastructure.profile_parsers import TOMLProfileParser
from shtym.infrastructure.profile_repositories import (
    BuiltinDefaultProfileRepository,
    FileBasedProfileRepository,
    MultiSourceProfileRepository,
)


class ProfileRepositoryFactory:
    """Factory for creating profile repositories with multi-source support."""

    @classmethod
    def create(cls) -> ProfileRepository:
        """Create a profile repository.

        Returns:
            ProfileRepository instance with multi-source support.
        """
        toml_parser = TOMLProfileParser()

        return MultiSourceProfileRepository(
            repositories=[
                FileBasedProfileRepository(
                    file_reader=FileReader(file_path=Path(".shtym") / "profiles.toml"),
                    parser=toml_parser,
                ),
                FileBasedProfileRepository(
                    file_reader=FileReader(
                        file_path=Path.home() / ".config" / "shtym" / "profiles.toml"
                    ),
                    parser=toml_parser,
                ),
                BuiltinDefaultProfileRepository(),
            ]
        )
