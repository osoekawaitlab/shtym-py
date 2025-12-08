"""LLM client factory module."""

import importlib
from typing import TYPE_CHECKING, cast

from shtym.domain.processor import ProcessorCreationError
from shtym.exceptions import LLMModuleNotFoundError
from shtym.infrastructure.llm_profile import (
    BaseLLMClientSettings,
    OllamaLLMClientSettings,
)

if TYPE_CHECKING:
    from shtym.infrastructure.processors.llm_processor import LLMClient


class LLMClientFactory:
    """Factory that creates LLM clients from LLM client settings."""

    def create(self, profile: BaseLLMClientSettings) -> "LLMClient":
        """Create an LLM client from the given settings.

        Args:
            profile: LLM client settings.

        Returns:
            LLM client instance.

        Raises:
            LLMModuleNotFoundError: If required LLM module not found.
            ProcessorCreationError: If unsupported settings type.
        """
        if isinstance(profile, OllamaLLMClientSettings):
            try:
                ollama_client_module = importlib.import_module(
                    "shtym.infrastructure.llm_clients.ollama_client"
                )
                client = cast(
                    "LLMClient",
                    ollama_client_module.OllamaLLMClient.create(settings=profile),
                )
            except ImportError as e:
                module_name = "ollama"
                raise LLMModuleNotFoundError(module_name) from e
            if client.is_available():
                return client
            # Client was created but is unavailable
            msg = f"LLM client is unavailable: {type(profile).__name__}"
            raise ProcessorCreationError(msg)

        # Profile type is not supported
        msg = f"Unsupported LLM settings type: {type(profile).__name__}"
        raise ProcessorCreationError(msg)
