"""Test suite for processor domain logic."""

from unittest.mock import MagicMock

from shtym.domain import processor as processor_module
from shtym.domain.profile import Profile, ProfileNotFoundError, ProfileRepository


def test_passthrough_processor_returns_input_unchanged() -> None:
    """Test that PassThroughProcessor returns input text unchanged."""
    sut = processor_module.PassThroughProcessor()
    execution = processor_module.CommandExecution(
        command=["echo", "test"],
        stdout="test input text\n",
        stderr="",
    )

    result = sut.process(execution)

    assert result == "test input text\n"


def test_passthrough_processor_handles_empty_string() -> None:
    """Test that PassThroughProcessor handles empty string."""
    sut = processor_module.PassThroughProcessor()
    execution = processor_module.CommandExecution(
        command=["echo"],
        stdout="",
        stderr="",
    )

    result = sut.process(execution)

    assert result == ""


def test_passthrough_processor_handles_multiline() -> None:
    """Test that PassThroughProcessor handles multiline text."""
    sut = processor_module.PassThroughProcessor()
    input_text = "line 1\nline 2\nline 3\n"
    execution = processor_module.CommandExecution(
        command=["echo", "multiline"],
        stdout=input_text,
        stderr="",
    )

    result = sut.process(execution)

    assert result == input_text


def test_passthrough_processor_is_always_available() -> None:
    """Test that PassThroughProcessor is always available."""
    sut = processor_module.PassThroughProcessor()

    assert sut.is_available() is True


class TestFallbackProcessor:
    """Test suite for FallbackProcessor."""

    def test_returns_wrapped_processor_result_on_success(self) -> None:
        """Test that FallbackProcessor returns wrapped processor result on success."""

        class MockProcessor:
            def process(self, execution: processor_module.CommandExecution) -> str:
                return f"processed output for {execution.command[0]}"

            def is_available(self) -> bool:
                return True

        wrapped = MockProcessor()
        sut = processor_module.FallbackProcessor(wrapped)
        execution = processor_module.CommandExecution(
            command=["test"],
            stdout="input",
            stderr="",
        )

        result = sut.process(execution)

        assert result == "processed output for test"

    def test_falls_back_to_passthrough_on_processing_error(self) -> None:
        """Test that FallbackProcessor falls back to PassThrough on ProcessingError."""

        class FailingProcessor:
            def process(self, execution: processor_module.CommandExecution) -> str:
                mesg = "Simulated processing failure"
                raise processor_module.ProcessingError(
                    mesg, execution=execution, cause=ValueError(mesg)
                )

            def is_available(self) -> bool:
                return True

        wrapped = FailingProcessor()
        sut = processor_module.FallbackProcessor(wrapped)
        execution = processor_module.CommandExecution(
            command=["test"],
            stdout="original input",
            stderr="",
        )

        result = sut.process(execution)

        assert result == "original input"

    def test_delegates_is_available_to_wrapped_processor(self) -> None:
        """Test that FallbackProcessor delegates is_available to wrapped processor."""

        class UnavailableProcessor:
            def process(self, execution: processor_module.CommandExecution) -> str:
                return execution.stdout

            def is_available(self) -> bool:
                return False

        wrapped = UnavailableProcessor()
        sut = processor_module.FallbackProcessor(wrapped)

        assert sut.is_available() is False


class TestCreateProcessorWithFallback:
    """Test suite for create_processor_with_fallback function."""

    def test_returns_fallback_wrapped_processor_when_available(self) -> None:
        """Test returns FallbackProcessor when factory creates available processor."""
        profile = MagicMock(spec=Profile)
        processor = MagicMock(spec=processor_module.Processor)
        processor.is_available.return_value = True
        factory = MagicMock(spec=processor_module.ProcessorFactory)
        factory.create.return_value = processor

        result = processor_module.create_processor_with_fallback(
            profile=profile, processor_factory=factory
        )

        assert isinstance(result, processor_module.FallbackProcessor)
        factory.create.assert_called_once_with(profile=profile)
        processor.is_available.assert_called_once_with()

    def test_returns_passthrough_when_processor_unavailable(self) -> None:
        """Test returns PassThrough when created processor is unavailable."""
        profile = MagicMock(spec=Profile)
        processor = MagicMock(spec=processor_module.Processor)
        processor.is_available.return_value = False
        factory = MagicMock(spec=processor_module.ProcessorFactory)
        factory.create.return_value = processor

        result = processor_module.create_processor_with_fallback(
            profile=profile, processor_factory=factory
        )

        assert isinstance(result, processor_module.PassThroughProcessor)
        factory.create.assert_called_once_with(profile=profile)
        processor.is_available.assert_called_once_with()

    def test_returns_passthrough_on_processor_creation_error(self) -> None:
        """Test returns PassThrough when factory raises ProcessorCreationError."""
        profile = MagicMock(spec=Profile)
        factory = MagicMock(spec=processor_module.ProcessorFactory)
        msg = "Creation failed"
        factory.create.side_effect = processor_module.ProcessorCreationError(msg)

        result = processor_module.create_processor_with_fallback(
            profile=profile, processor_factory=factory
        )

        assert isinstance(result, processor_module.PassThroughProcessor)
        factory.create.assert_called_once_with(profile=profile)


class TestCreateProcessorFromProfileName:
    """Test suite for create_processor_from_profile_name function."""

    def test_returns_processor_when_profile_found(self) -> None:
        """Test returns processor when profile is found and processor created."""
        profile = MagicMock(spec=Profile)
        repository = MagicMock(spec=ProfileRepository)
        repository.get.return_value = profile
        processor = MagicMock(spec=processor_module.Processor)
        processor.is_available.return_value = True
        factory = MagicMock(spec=processor_module.ProcessorFactory)
        factory.create.return_value = processor

        result = processor_module.create_processor_from_profile_name(
            profile_name="test-profile",
            profile_repository=repository,
            processor_factory=factory,
        )

        assert isinstance(result, processor_module.FallbackProcessor)
        repository.get.assert_called_once_with(name="test-profile")
        factory.create.assert_called_once_with(profile=profile)
        processor.is_available.assert_called_once_with()

    def test_returns_passthrough_when_profile_not_found(self) -> None:
        """Test returns PassThrough when profile is not found."""
        repository = MagicMock(spec=ProfileRepository)
        factory = MagicMock(spec=processor_module.ProcessorFactory)
        repository.get.side_effect = ProfileNotFoundError("nonexistent")

        result = processor_module.create_processor_from_profile_name(
            profile_name="nonexistent",
            profile_repository=repository,
            processor_factory=factory,
        )

        assert isinstance(result, processor_module.PassThroughProcessor)
        repository.get.assert_called_once_with(name="nonexistent")
        factory.create.assert_not_called()
