"""Test suite for LLM client factory implementation."""

from pytest_mock import MockerFixture

from shtym.infrastructure.llm_clients.factory import LLMClientFactory
from shtym.infrastructure.llm_profile import OllamaLLMClientSettings


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
