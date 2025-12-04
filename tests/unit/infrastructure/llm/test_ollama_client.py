"""Test suite for Ollama LLM client."""

import pytest
from pytest_mock import MockerFixture

try:
    from shtym.infrastructure import ollama_client as ollama_client_module

    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    ollama_client_module = None  # type: ignore[assignment]

pytestmark = pytest.mark.skipif(not OLLAMA_AVAILABLE, reason="ollama not installed")


def test_ollama_client_chat_success(mocker: MockerFixture) -> None:
    """Test that OllamaLLMClient.chat returns LLM response successfully."""
    client = mocker.Mock()
    response = mocker.Mock()
    response.message.content = "LLM response"
    client.chat.return_value = response

    sut = ollama_client_module.OllamaLLMClient(client=client, model="gpt-oss:20b")

    result = sut.chat(system_prompt="system", user_prompt="user", error_message="error")

    client.chat.assert_called_once()
    call_args = client.chat.call_args
    assert call_args.kwargs["model"] == "gpt-oss:20b"
    messages = call_args.kwargs["messages"]
    expected_message_count = 3
    assert len(messages) == expected_message_count
    assert messages[0].role == "system"
    assert messages[0].content == "system"
    assert messages[1].role == "user"
    assert messages[1].content == "user"
    assert messages[2].role == "user"
    assert messages[2].content == "error"
    assert result == "LLM response"


def test_ollama_client_chat_without_error(mocker: MockerFixture) -> None:
    """Test that OllamaLLMClient.chat works without error_message."""
    client = mocker.Mock()
    response = mocker.Mock()
    response.message.content = "LLM response"
    client.chat.return_value = response

    sut = ollama_client_module.OllamaLLMClient(client=client, model="gpt-oss:20b")

    result = sut.chat(system_prompt="system", user_prompt="user")

    messages = client.chat.call_args.kwargs["messages"]
    expected_message_count = 2
    assert len(messages) == expected_message_count
    assert result == "LLM response"


def test_ollama_client_chat_returns_empty_on_none_content(
    mocker: MockerFixture,
) -> None:
    """Test that OllamaLLMClient.chat returns empty string when content is None."""
    client = mocker.Mock()
    response = mocker.Mock()
    response.message.content = None
    client.chat.return_value = response

    sut = ollama_client_module.OllamaLLMClient(client=client, model="gpt-oss:20b")

    result = sut.chat(system_prompt="system", user_prompt="user")

    assert result == ""


def test_ollama_client_is_available_returns_true(mocker: MockerFixture) -> None:
    """Test that OllamaLLMClient.is_available returns True when model exists."""
    client = mocker.Mock()
    model1 = mocker.Mock()
    model1.model = "gpt-oss:20b"
    model2 = mocker.Mock()
    model2.model = "other-model"
    models_response = mocker.Mock()
    models_response.models = [model1, model2]
    client.list.return_value = models_response

    sut = ollama_client_module.OllamaLLMClient(client=client, model="gpt-oss:20b")

    assert sut.is_available() is True


def test_ollama_client_is_available_returns_false_when_model_missing(
    mocker: MockerFixture,
) -> None:
    """Test that OllamaLLMClient.is_available returns False when model missing."""
    client = mocker.Mock()
    model = mocker.Mock()
    model.model = "other-model"
    models_response = mocker.Mock()
    models_response.models = [model]
    client.list.return_value = models_response

    sut = ollama_client_module.OllamaLLMClient(client=client, model="gpt-oss:20b")

    assert sut.is_available() is False


def test_ollama_client_is_available_returns_false_on_connection_error(
    mocker: MockerFixture,
) -> None:
    """Test that OllamaLLMClient.is_available returns False on connection error."""
    client = mocker.Mock()
    client.list.side_effect = ConnectionError("Connection failed")

    sut = ollama_client_module.OllamaLLMClient(client=client, model="gpt-oss:20b")

    assert sut.is_available() is False


def test_ollama_client_create_uses_custom_model_from_env(
    mocker: MockerFixture,
) -> None:
    """Test that OllamaLLMClient.create uses SHTYM_LLM_SETTINGS__MODEL env var."""
    mocker.patch.dict("os.environ", {"SHTYM_LLM_SETTINGS__MODEL": "llama2"})
    mocker.patch("shtym.infrastructure.ollama_client.Client")

    sut = ollama_client_module.OllamaLLMClient.create()

    # Verify model is set correctly
    assert sut.model == "llama2"


@pytest.mark.parametrize(
    "env_value",
    [
        None,  # env var not set
        "",  # empty string
        "   ",  # whitespace only
    ],
)
def test_ollama_client_create_defaults_to_gpt_oss_20b(
    mocker: MockerFixture, env_value: str | None
) -> None:
    """Test OllamaLLMClient.create defaults when env var not set or empty."""
    if env_value is None:
        mocker.patch.dict("os.environ", {}, clear=True)
    else:
        mocker.patch.dict("os.environ", {"SHTYM_LLM_SETTINGS__MODEL": env_value})
    mocker.patch("shtym.infrastructure.ollama_client.Client")

    sut = ollama_client_module.OllamaLLMClient.create()

    assert sut.model == "gpt-oss:20b"
