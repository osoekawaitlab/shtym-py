"""LLM-based profile implementation."""

import os

from pydantic import BaseModel, Field


class LLMSettings(BaseModel):
    """LLM service settings."""

    model_name: str = Field(
        default="llama3.2:3b",
        description="LLM model name",
    )
    base_url: str = Field(
        default="http://localhost:11434",
        description="LLM service base URL",
    )


class LLMProfile(BaseModel):
    """Profile for LLM-based output transformation."""

    prompt_template: str = Field(
        default=(
            "Your task is to summarize and distill the essential information "
            "from command output."
        ),
        description="Prompt template for LLM processing",
    )
    llm_settings: LLMSettings = Field(
        default_factory=LLMSettings,
        description="LLM service settings",
    )

    @property
    def model_name(self) -> str:
        """Get the LLM model name.

        Returns:
            The model name string.
        """
        return self.llm_settings.model_name

    @property
    def base_url(self) -> str:
        """Get the LLM service base URL.

        Returns:
            The base URL string.
        """
        return self.llm_settings.base_url

    @classmethod
    def from_env(cls) -> "LLMProfile":
        """Create LLMProfile from environment variables.

        Environment variables:
            SHTYM_LLM_SETTINGS__MODEL: LLM model name
            SHTYM_LLM_SETTINGS__BASE_URL: LLM service base URL

        Returns:
            LLMProfile instance with settings from environment.
        """
        llm_settings = LLMSettings(
            model_name=os.environ.get(
                "SHTYM_LLM_SETTINGS__MODEL", LLMSettings().model_name
            ),
            base_url=os.environ.get(
                "SHTYM_LLM_SETTINGS__BASE_URL", LLMSettings().base_url
            ),
        )
        return cls(llm_settings=llm_settings)
