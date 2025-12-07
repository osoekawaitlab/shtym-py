"""Processor factory implementation."""

import importlib

from shtym.domain.processor import Processor, ProcessorCreationError
from shtym.domain.profile import Profile
from shtym.exceptions import LLMModuleNotFoundError
from shtym.infrastructure.llm_profile import LLMProfile
from shtym.infrastructure.processors.llm_processor import LLMProcessor


class ConcreteProcessorFactory:
    """Factory that creates actual processors from profiles."""

    def create(self, profile: Profile) -> Processor:
        """Create a processor from the given profile.

        Args:
            profile: Profile to create processor.

        Returns:
            Processor instance.

        Raises:
            ProcessorCreationError: If processor creation fails.
        """
        if isinstance(profile, LLMProfile):
            return LLMProcessor.create(profile=profile)

        msg = f"Unsupported profile type: {type(profile).__name__}"
        raise ProcessorCreationError(msg)


class LLMProcessorFactory:
    """Factory that creates LLM processors from LLM profiles."""

    def create(self, profile: LLMProfile) -> Processor:
        """Create an LLM processor from the given LLM profile.

        Args:
            profile: LLM profile to create processor from.

        Returns:
            Processor instance.

        Raises:
            ProcessorCreationError: If processor creation fails.
        """
        try:
            target_module_name = "ollama"
            ollama = importlib.import_module(target_module_name)
            ollama_client_module = importlib.import_module(
                "shtym.infrastructure.llm_clients.ollama_client"
            )
        except ImportError as e:
            raise LLMModuleNotFoundError(target_module_name) from e
        client = ollama.Client(host=str(profile.llm_settings.base_url))
        llm_client = ollama_client_module.OllamaLLMClient(
            client=client, model=profile.llm_settings.model_name
        )
        return LLMProcessor(
            llm_client=llm_client,
            prompt_template=profile.prompt_template,
        )
