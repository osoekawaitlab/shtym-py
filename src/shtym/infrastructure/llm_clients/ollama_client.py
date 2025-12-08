"""Ollama-specific LLM client implementation.

Implements the LLMClient protocol defined in processors.llm_processor.
"""

from typing import TYPE_CHECKING

from ollama import Client, Message
from ollama import ResponseError as OllamaResponseError

if TYPE_CHECKING:
    from shtym.infrastructure.llm_profile import OllamaLLMClientSettings


class OllamaLLMClient:
    """LLM client implementation using Ollama."""

    DEFAULT_MODEL = "gpt-oss:20b"

    def __init__(self, client: Client, model: str) -> None:
        """Initialize the Ollama LLM client.

        Args:
            client: An instance of the Ollama Client.
            model: The name of the Ollama model to use.
        """
        self.client = client
        self.model = model

    def chat(
        self, system_prompt: str, user_prompt: str, error_message: str = ""
    ) -> str:
        """Send a chat request to Ollama.

        Args:
            system_prompt: The system prompt to set context for the LLM.
            user_prompt: The main user message/prompt.
            error_message: Optional error message to include in the conversation.

        Returns:
            The LLM's response as a string.

        Raises:
            OllamaResponseError: If Ollama returns an error response.
            ConnectionError: If Ollama cannot be reached.
        """
        messages = [
            Message(role="system", content=system_prompt),
            Message(role="user", content=user_prompt),
        ]
        if error_message.strip():
            messages.append(Message(role="user", content=error_message))

        response = self.client.chat(model=self.model, messages=messages)
        result = response.message.content
        if result is None:
            return ""
        return result

    def is_available(self) -> bool:
        """Check if Ollama is available and has the required model.

        Returns:
            True if Ollama can be used, False otherwise.
        """
        try:
            model_names = {model.model for model in self.client.list().models}
        except (OllamaResponseError, ConnectionError):
            return False
        else:
            return self.model in model_names

    @classmethod
    def create(cls, settings: "OllamaLLMClientSettings") -> "OllamaLLMClient":
        """Factory method to create an OllamaLLMClient from settings.

        Args:
            settings: Ollama LLM client settings.

        Returns:
            An instance of OllamaLLMClient.
        """
        model = settings.model_name.strip()
        if not model:
            model = cls.DEFAULT_MODEL

        client = Client(host=str(settings.base_url))
        return cls(client=client, model=model)
