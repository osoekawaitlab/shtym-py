"""Processor domain protocols and implementations."""

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from shtym.domain.llm_client import LLMClient


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


class LLMProcessor:
    """Processor that uses LLM for output processing.

    This processor depends on the LLMClient protocol, which abstracts away
    the specific LLM provider (Ollama, OpenAI, Claude, etc.).
    """

    def __init__(self, llm_client: "LLMClient") -> None:
        """Initialize the LLM processor with an LLM client.

        Args:
            llm_client: An instance implementing the LLMClient protocol.
        """
        self.llm_client = llm_client

    def process(self, command: list[str], stdout: str, stderr: str) -> str:
        """Process the output text using LLM.

        Falls back to raw stdout if LLM is unavailable or fails.

        Args:
            command: The command and its arguments as a list.
            stdout: The standard output from the command.
            stderr: The standard error output from the command.

        Returns:
            The processed text, or raw stdout if LLM fails.
        """
        system_prompt = (
            "Your task is to summarize and distill the essential information"
            f" from the command '{' '.join(command)}':\n\n"
            "The provided user message is the raw output of the command so it may"
            " contain extraneous information, errors, or formatting artifacts."
            " Your goal is to extract the most relevant and accurate information."
            " Also, error will be provided if any as a separate user message."
        )
        try:
            result: str = self.llm_client.chat(
                system_prompt=system_prompt, user_prompt=stdout, error_message=stderr
            )
        except Exception:  # noqa: BLE001
            # Fall back to raw output if LLM fails
            return stdout
        else:
            return result

    def is_available(self) -> bool:
        """Check if LLM is available for use.

        Returns:
            True if LLM can be used, False otherwise.
        """
        available: bool = self.llm_client.is_available()
        return available
