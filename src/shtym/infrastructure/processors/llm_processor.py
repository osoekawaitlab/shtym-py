"""LLM-based processor implementation."""

from string import Template
from typing import Protocol

from shtym.domain.processor import CommandExecution
from shtym.infrastructure.llm_clients.factory import LLMClientFactory
from shtym.infrastructure.llm_profile import LLMProfile


class LLMClient(Protocol):
    """Protocol for LLM client interactions.

    This protocol abstracts away the specific LLM provider (Ollama, OpenAI,
    Claude, etc.) within the infrastructure layer.
    """

    def chat(
        self, system_prompt: str, user_prompt: str, error_message: str = ""
    ) -> str:
        """Send a chat request to the LLM.

        Args:
            system_prompt: The system prompt to set context for the LLM.
            user_prompt: The main user message/prompt.
            error_message: Optional error message to include in the conversation.

        Returns:
            The LLM's response as a string.
        """

    def is_available(self) -> bool:
        """Check if the LLM client is available and ready to use.

        Returns:
            True if the client can be used, False otherwise.
        """


class LLMProcessor:
    """Processor that uses LLM for output processing.

    This processor depends on the LLMClient protocol, which abstracts away
    the specific LLM provider (Ollama, OpenAI, Claude, etc.).
    """

    def __init__(self, llm_client: LLMClient, prompt_template: str) -> None:
        """Initialize the LLM processor with an LLM client and prompt template.

        Args:
            llm_client: An instance implementing the LLMClient protocol.
            prompt_template: Template string for system prompt (uses
                string.Template format).
        """
        self.llm_client = llm_client
        self.prompt_template = prompt_template

    def process(self, execution: CommandExecution) -> str:
        """Process the command execution output using LLM.

        Falls back to raw stdout if LLM is unavailable or fails.

        Args:
            execution: The command execution containing command and its output.

        Returns:
            The processed text, or raw stdout if LLM fails.
        """
        template = Template(self.prompt_template)
        system_prompt = template.substitute(command=" ".join(execution.command))
        try:
            result: str = self.llm_client.chat(
                system_prompt=system_prompt,
                user_prompt=execution.stdout,
                error_message=execution.stderr,
            )
        except Exception:  # noqa: BLE001
            # Fall back to raw output if LLM fails
            return execution.stdout
        else:
            return result

    def is_available(self) -> bool:
        """Check if LLM is available for use.

        Returns:
            True if LLM can be used, False otherwise.
        """
        available: bool = self.llm_client.is_available()
        return available

    @classmethod
    def create(cls, profile: LLMProfile) -> "LLMProcessor":
        """Create an LLMProcessor from the given LLM profile.

        Args:
            profile: LLM profile to create processor from.

        Returns:
            LLMProcessor instance.
        """
        llm_client_factory = LLMClientFactory()
        llm_client = llm_client_factory.create(profile=profile.llm_settings)
        return cls(llm_client=llm_client, prompt_template=profile.prompt_template)
