"""LLM-based profile implementation."""

import os
from typing import Literal

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

    type: Literal["llm"] = Field(default="llm", description="Profile type identifier")
    version: int = Field(default=1, description="Profile schema version")
    system_prompt_template: str = Field(
        default=(
            "Your task is to summarize and distill the essential information "
            "from the command $command."
        ),
        description="System prompt template (sets LLM context)",
    )
    user_prompt_template: str = Field(
        default=(
            "The provided message is the raw output of the command. "
            "It may contain extraneous information, errors, or formatting artifacts. "
            "Extract the most relevant and accurate information.\n\n"
            "Output:\n$stdout\n\nErrors:\n$stderr"
        ),
        description="User prompt template (contains command output)",
    )
    llm_settings: LLMSettings = Field(
        default_factory=OllamaLLMClientSettings,
        description="LLM service settings",
    )
