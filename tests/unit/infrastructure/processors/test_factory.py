"""Test suite for processor factory implementation."""

from pytest_mock import MockerFixture

from shtym.infrastructure.llm_profile import LLMProfile
from shtym.infrastructure.processors.factory import ConcreteProcessorFactory


def test_create_delegates_to_llm_processor_create_for_llm_profile(
    mocker: MockerFixture,
) -> None:
    """Test that create delegates to LLMProcessor.create when given LLMProfile."""
    profile = LLMProfile()
    mock_llm_processor_create = mocker.patch(
        "shtym.infrastructure.processors.factory.LLMProcessor.create"
    )
    factory = ConcreteProcessorFactory()

    result = factory.create(profile=profile)

    mock_llm_processor_create.assert_called_once_with(profile=profile)
    assert result == mock_llm_processor_create.return_value
