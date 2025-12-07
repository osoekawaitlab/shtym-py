"""LLM client protocol for domain layer."""

from typing import Protocol


class LLMClient(Protocol):
    """Protocol for LLM client interactions.

    This protocol abstracts away the specific LLM provider (Ollama, OpenAI,
    Claude, etc.) and defines the interface that domain layer expects.
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
