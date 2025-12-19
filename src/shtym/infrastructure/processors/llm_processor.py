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

    def __init__(
        self,
        llm_client: LLMClient,
        system_prompt_template: str,
        user_prompt_template: str,
    ) -> None:
        """Initialize the LLM processor with an LLM client and prompt templates.

        Args:
            llm_client: An instance implementing the LLMClient protocol.
            system_prompt_template: Template string for system prompt (uses
                string.Template format).
            user_prompt_template: Template string for user prompt (uses
                string.Template format).
        """
        self.llm_client = llm_client
        self.system_prompt_template = system_prompt_template
        self.user_prompt_template = user_prompt_template

    def process(self, execution: CommandExecution) -> str:
        """Process the command execution output using LLM.

        Falls back to raw stdout if LLM is unavailable or fails.

        Args:
            execution: The command execution containing command and its output.

        Returns:
            The processed text, or raw stdout if LLM fails.
        """
        command_str = " ".join(execution.command)

        # Both templates can use all available variables for flexibility
        template_vars = {
            "command": command_str,
            "stdout": execution.stdout,
            "stderr": execution.stderr,
        }

        system_template = Template(self.system_prompt_template)
        system_prompt = system_template.substitute(**template_vars)

        user_template = Template(self.user_prompt_template)
        user_prompt = user_template.substitute(**template_vars)

        try:
            result: str = self.llm_client.chat(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                error_message="",  # Now included in user_prompt template
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
        return cls(
            llm_client=llm_client,
            system_prompt_template=profile.system_prompt_template,
            user_prompt_template=profile.user_prompt_template,
        )
