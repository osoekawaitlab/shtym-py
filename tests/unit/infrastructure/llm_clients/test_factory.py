"""Test suite for LLM client factory implementation."""

import pytest
from pytest_mock import MockerFixture

from shtym.domain.processor import ProcessorCreationError
from shtym.infrastructure.llm_clients.factory import LLMClientFactory
from shtym.infrastructure.llm_profile import (
    BaseLLMClientSettings,
    OllamaLLMClientSettings,
)


def test_create_delegates_to_ollama_client_create(mocker: MockerFixture) -> None:
    """Test that create delegates to OllamaLLMClient.create."""
    settings = OllamaLLMClientSettings()
    mock_ollama_client_module = mocker.patch(
        "shtym.infrastructure.llm_clients.factory.importlib.import_module"
    )
    mock_module = mocker.MagicMock()
    mock_ollama_client_module.return_value = mock_module

    factory = LLMClientFactory()

    result = factory.create(profile=settings)

    mock_ollama_client_module.assert_called_once_with(
        "shtym.infrastructure.llm_clients.ollama_client"
    )
    mock_module.OllamaLLMClient.create.assert_called_once_with(settings=settings)
    assert result == mock_module.OllamaLLMClient.create.return_value


def test_create_raises_error_when_client_unavailable(mocker: MockerFixture) -> None:
    """Test that create raises ProcessorCreationError when client is unavailable."""
    settings = OllamaLLMClientSettings()
    mock_ollama_client_module = mocker.patch(
        "shtym.infrastructure.llm_clients.factory.importlib.import_module"
    )
    mock_module = mocker.MagicMock()
    mock_ollama_client_module.return_value = mock_module
    # Client is created but unavailable
    mock_client = mock_module.OllamaLLMClient.create.return_value
    mock_client.is_available.return_value = False

    factory = LLMClientFactory()

    with pytest.raises(
        ProcessorCreationError,
        match="LLM client is unavailable: OllamaLLMClientSettings",
    ):
        factory.create(profile=settings)


def test_create_raises_error_for_unsupported_settings_type() -> None:
    """Test that create raises ProcessorCreationError for unsupported type."""

    class UnsupportedSettings(BaseLLMClientSettings):
        """Unsupported settings type."""

    settings = UnsupportedSettings()
    factory = LLMClientFactory()

    with pytest.raises(
        ProcessorCreationError,
        match="Unsupported LLM settings type: UnsupportedSettings",
    ):
        factory.create(profile=settings)
