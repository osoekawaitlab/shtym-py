"""LLM-based profile implementation."""

import os

from pydantic import AnyHttpUrl, Field

from shtym.domain.processor import ShtymBaseModel


class BaseLLMClientSettings(ShtymBaseModel):
    """LLM client settings."""


class OllamaLLMClientSettings(BaseLLMClientSettings):
    """Ollama LLM client settings."""

    model_name: str = Field(
        default=os.getenv("SHTYM_LLM_SETTINGS__MODEL", "gpt-oss:20b"),
        description="Ollama model name",
    )
    base_url: AnyHttpUrl = Field(
        default=AnyHttpUrl(
            os.getenv("SHTYM_LLM_SETTINGS__BASE_URL", "http://localhost:11434")
        ),
        description="Ollama service base URL",
    )


LLMSettings = OllamaLLMClientSettings


class LLMProfile(ShtymBaseModel):
    """Profile for LLM-based output transformation."""

    prompt_template: str = Field(
        default=(
            "Your task is to summarize and distill the essential information"
            " from the command $command:\n\n"
            "The provided user message is the raw output of the command so it may"
            " contain extraneous information, errors, or formatting artifacts."
            " Your goal is to extract the most relevant and accurate information."
            " Also, error will be provided if any as a separate user message."
        ),
        description="Prompt template for LLM processing",
    )
    llm_settings: LLMSettings = Field(
        default_factory=OllamaLLMClientSettings,
        description="LLM service settings",
    )
