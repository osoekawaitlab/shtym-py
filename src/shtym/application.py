"""Application layer for shtym."""

import importlib
import subprocess
from dataclasses import dataclass
from typing import TYPE_CHECKING

from shtym.domain.processor import PassThroughProcessor, Processor
from shtym.domain.profile import ProfileNotFoundError

if TYPE_CHECKING:
    from shtym.domain.profile import ProfileRepository


@dataclass
class ProcessedCommandResult:
    """Result of processing a command with a processor."""

    processed_output: str
    stderr: str
    returncode: int


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
            command=command, stdout=result.stdout, stderr=result.stderr
        )
        return ProcessedCommandResult(
            processed_output=processed_output,
            stderr=result.stderr,
            returncode=result.returncode,
        )

    @classmethod
    def create(
        cls,
        profile_repository: "ProfileRepository",
        profile_name: str,
    ) -> "ShtymApplication":
        """Factory method to create a ShtymApplication with the appropriate processor.

        Args:
            profile_repository: Repository to get profiles from.
            profile_name: Name of the profile to use.

        Returns:
            An instance of ShtymApplication.
        """
        # Try to get the profile
        try:
            profile_repository.get(profile_name)
            # Profile found, but we don't use it yet - fall through to LLM logic
        except ProfileNotFoundError:
            # Profile not found, use PassThroughProcessor
            return cls(processor=PassThroughProcessor())

        try:
            processor_module = importlib.import_module("shtym.domain.processor")
            ollama_module = importlib.import_module(
                "shtym.infrastructure.ollama_client"
            )

            llm_client = ollama_module.OllamaLLMClient.create()
            if llm_client.is_available():
                processor: Processor = processor_module.LLMProcessor(
                    llm_client=llm_client
                )
            else:
                processor = PassThroughProcessor()
        except ModuleNotFoundError:
            # Ollama not installed, fall back to PassThroughProcessor
            processor = PassThroughProcessor()
        return cls(processor=processor)
