"""Processor domain protocols and implementations."""

from typing import Protocol


class Processor(Protocol):
    """Protocol for output processing strategies."""

    def process(self, command: list[str], stdout: str, stderr: str) -> str:
        """Process the output text.

        Args:
            command: The command and its arguments as a list.
            stdout: The standard output from the command.
            stderr: The standard error output from the command.

        Returns:
            The processed text.
        """

    def is_available(self) -> bool:
        """Check if the processor is available for use.

        Returns:
            True if the processor can be used, False otherwise.
        """


class PassThroughProcessor:
    """Processor that passes text through unchanged.

    This is the default processor used when LLM integration is not configured.
    """

    def process(self, command: list[str], stdout: str, stderr: str) -> str:  # noqa: ARG002
        """Return the output text unchanged.

        Args:
            command: The command and its arguments as a list.
            stdout: The standard output from the command.
            stderr: The standard error output from the command.

        Returns:
            The same text without modification.
        """
        return stdout

    def is_available(self) -> bool:
        """The pass-through processor is always available.

        Returns:
            True
        """
        return True
