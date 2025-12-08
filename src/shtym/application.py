"""Application layer for shtym."""

import subprocess

from shtym.domain.processor import (
    CommandExecution,
    ProcessedCommandResult,
    Processor,
    create_processor_from_profile_name,
)
from shtym.infrastructure.processors.factory import ConcreteProcessorFactory
from shtym.infrastructure.profile_repository import FileBasedProfileRepository


class ShtymApplication:
    """Main application class for shtym."""

    def __init__(self, processor: Processor) -> None:
        """Initialize the application with an output processor.

        Args:
            processor: The processor to apply to command outputs.
        """
        self.processor = processor

    def run_command(self, command: list[str]) -> subprocess.CompletedProcess[str]:
        """Execute a command as a subprocess.

        Args:
            command: The command and its arguments as a list.

        Returns:
            The completed process result.
        """
        return subprocess.run(  # noqa: S603
            command, capture_output=True, text=True, check=False
        )

    def process_command(self, command: list[str]) -> ProcessedCommandResult:
        """Execute a command and apply the processor to its output.

        Args:
            command: The command and its arguments as a list.

        Returns:
            The processed command result with processed output, stderr, and return code.
        """
        result = self.run_command(command)
        processed_output = self.processor.process(
            CommandExecution(
                command=command,
                stdout=result.stdout,
                stderr=result.stderr,
            )
        )
        return ProcessedCommandResult(
            processed_output=processed_output,
            stderr=result.stderr,
            returncode=result.returncode,
        )

    @classmethod
    def create(
        cls,
        profile_name: str,
    ) -> "ShtymApplication":
        """Factory method to create a ShtymApplication with the appropriate processor.

        Args:
            profile_name: Name of the profile to use.

        Returns:
            An instance of ShtymApplication.
        """
        profile_repository = FileBasedProfileRepository()
        processor_factory = ConcreteProcessorFactory()
        return cls(
            create_processor_from_profile_name(
                profile_name=profile_name,
                profile_repository=profile_repository,
                processor_factory=processor_factory,
            )
        )
