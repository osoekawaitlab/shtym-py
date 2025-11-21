"""Filter implementations for text processing."""

from typing import Protocol


class Filter(Protocol):
    """Protocol for text filtering strategies."""

    def filter(self, text: str) -> str:
        """Filter the input text.

        Args:
            text: The input text to filter.

        Returns:
            The filtered text.
        """
        ...


class PassThroughFilter:
    """Filter that passes text through unchanged.

    This is the default filter used when LLM integration is not configured.
    """

    def filter(self, text: str) -> str:
        """Return the input text unchanged.

        Args:
            text: The input text to filter.

        Returns:
            The same text without modification.
        """
        return text
