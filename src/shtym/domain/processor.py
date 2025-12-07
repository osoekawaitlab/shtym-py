"""Processor domain protocols and implementations."""

from typing import Protocol

from pydantic import BaseModel

from shtym.domain.profile import Profile, ProfileNotFoundError, ProfileRepository
from shtym.exceptions import ShtymDomainError


class ShtymBaseModel(BaseModel):
    """Base model for domain objects with Pydantic integration."""


class CommandExecution(ShtymBaseModel):
    """Domain object representing a command execution with its output.

    This object unifies the command and its execution results (stdout/stderr)
    into a single cohesive domain concept.
    """

    command: list[str]
    stdout: str
    stderr: str


class ProcessedCommandResult(ShtymBaseModel):
    """Result of processing a command with a processor."""

    processed_output: str
    stderr: str
    returncode: int


class Processor(Protocol):
    """Protocol for output processing strategies."""

    def process(self, execution: CommandExecution) -> str:
        """Process the command execution output.

        Args:
            execution: The command execution containing command and its output.

        Returns:
            The processed text.
        """

    def is_available(self) -> bool:
        """Check if the processor is available for use.

        Returns:
            True if the processor can be used, False otherwise.
        """


class ProcessorCreationError(ShtymDomainError):
    """Raised when processor creation fails.

    This error indicates that a Processor could not be created from a Profile,
    typically due to missing dependencies or invalid configuration.
    """

    def __init__(self, message: str, *, cause: Exception | None = None) -> None:
        """Initialize the error.

        Args:
            message: Description of why processor creation failed.
            cause: The underlying exception that caused the failure, if any.
        """
        super().__init__(message)
        self.cause = cause


class ProcessingError(ShtymDomainError):
    """Raised when processor.process() fails.

    This error indicates that processing the output failed,
    and the system should fall back to PassThroughProcessor.
    """

    def __init__(
        self,
        message: str,
        *,
        execution: CommandExecution,
        cause: Exception | None = None,
    ) -> None:
        """Initialize the error.

        Args:
            message: Description of why processing failed.
            execution: The command execution that failed to process.
            cause: The underlying exception that caused the failure, if any.
        """
        super().__init__(message)
        self.execution = execution
        self.cause = cause


class ProcessorFactory(Protocol):
    """Protocol for creating processors from profiles."""

    def create(self, profile: Profile) -> Processor:
        """Create a processor from a profile.

        Args:
            profile: Profile to create processor from.

        Returns:
            Processor instance.

        Raises:
            ProcessorCreationError: If processor creation fails.
        """


class PassThroughProcessor:
    """Processor that passes text through unchanged.

    This is the default processor used when LLM integration is not configured.
    """

    def process(self, execution: CommandExecution) -> str:
        """Return the output text unchanged.

        Args:
            execution: The command execution containing command and its output.

        Returns:
            The stdout without modification.
        """
        return execution.stdout

    def is_available(self) -> bool:
        """The pass-through processor is always available.

        Returns:
            True
        """
        return True


class FallbackProcessor:
    """Processor that falls back to PassThrough on processing errors.

    This wrapper catches ProcessingError from the wrapped processor
    and retries with PassThroughProcessor to ensure output is always returned.
    """

    def __init__(self, processor: Processor) -> None:
        """Initialize with a processor to wrap.

        Args:
            processor: The processor to wrap with fallback behavior.
        """
        self._processor = processor

    def process(self, execution: CommandExecution) -> str:
        """Process output, falling back to PassThrough on error.

        Args:
            execution: The command execution containing command and its output.

        Returns:
            Processed text, or original stdout if processing fails.
        """
        try:
            return self._processor.process(execution)
        except ProcessingError:
            return PassThroughProcessor().process(execution)

    def is_available(self) -> bool:
        """Check if the wrapped processor is available.

        Returns:
            Result from the wrapped processor's is_available().
        """
        return self._processor.is_available()


def create_processor_with_fallback(
    profile: Profile,
    processor_factory: ProcessorFactory,
) -> Processor:
    """Create a processor from profile with fallback to PassThrough.

    If processor creation fails or the processor is unavailable,
    returns PassThroughProcessor. Otherwise, wraps the processor
    with FallbackProcessor for runtime error handling.

    Args:
        profile: Profile to create processor from.
        processor_factory: Factory to create processor from profile.

    Returns:
        Processor instance (either PassThrough or FallbackProcessor wrapping
        created processor).
    """
    try:
        processor = processor_factory.create(profile=profile)
        if not processor.is_available():
            return PassThroughProcessor()
        return FallbackProcessor(processor)
    except ProcessorCreationError:
        return PassThroughProcessor()


def create_processor_from_profile_name(
    profile_name: str,
    profile_repository: ProfileRepository,
    processor_factory: ProcessorFactory,
) -> Processor:
    """Create a processor from profile name with complete fallback handling.

    This function handles the complete flow:
    1. Resolve profile name to Profile via profile_repository
    2. Create processor from profile via processor_factory
    3. Wrap with fallback behavior

    Falls back to PassThroughProcessor if:
    - Profile not found
    - Processor creation fails
    - Processor is unavailable

    Args:
        profile_name: Name of the profile to load.
        profile_repository: Repository to retrieve profiles from.
        processor_factory: Factory to create processors from profiles.

    Returns:
        Processor instance ready to use (never fails).
    """
    try:
        profile = profile_repository.get(name=profile_name)
    except ProfileNotFoundError:
        return PassThroughProcessor()

    return create_processor_with_fallback(profile, processor_factory)
