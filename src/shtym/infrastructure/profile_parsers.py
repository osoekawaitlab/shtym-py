"""Profile parsers for shtym."""

import sys

from pydantic import ValidationError

from shtym.domain.profile import Profile
from shtym.exceptions import ShtymInfrastructureError
from shtym.infrastructure.llm_profile import LLMProfile

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


class ProfileParserError(ShtymInfrastructureError):
    """Exception raised when profile parsing fails."""

    def __init__(self, message: str) -> None:
        """Initialize the exception.

        Args:
            message: The error message.
        """
        super().__init__(f"Profile parsing error: {message}")


class TOMLProfileParser:
    """Parser for TOML formatted profile files."""

    def parse(self, content: str) -> dict[str, Profile]:
        """Parse the TOML content into a dictionary.

        Args:
            content: The TOML content as a string.

        Returns:
            A dictionary representation of the profiles.
        """
        try:
            parsed = tomllib.loads(content)
        except tomllib.TOMLDecodeError as e:
            raise ProfileParserError(str(e)) from e
        try:
            profiles = parsed["profiles"]
        except KeyError as e:
            msg = "Missing 'profiles' section in TOML"
            raise ProfileParserError(msg) from e
        if not isinstance(profiles, dict):
            msg = "'profiles' section must be a table"
            raise ProfileParserError(msg)
        result: dict[str, Profile] = {}
        try:
            for profile_name, profile_data in profiles.items():
                result[profile_name] = LLMProfile.model_validate(profile_data)
        except ValidationError as e:
            msg = f"Invalid profile data for '{profile_name}': {e}"
            raise ProfileParserError(msg) from e
        return result
