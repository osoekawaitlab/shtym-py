"""Application layer for shtym."""

import importlib
import subprocess
from dataclasses import dataclass

from shtym.domain.filter import Filter, PassThroughFilter


@dataclass
class ProcessedCommandResult:
    """Result of processing a command with a filter."""

    filtered_output: str
    stderr: str
    returncode: int


class ShtymApplication:
    """Main application class for shtym."""

    def __init__(self, text_filter: Filter) -> None:
        """Initialize the application with a text filter.

        Args:
            text_filter: The filter to apply to command outputs.
        """
        self.text_filter = text_filter

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
        """Execute a command and apply the filter to its output.

        Args:
            command: The command and its arguments as a list.

        Returns:
            The processed command result with filtered output, stderr, and return code.
        """
        result = self.run_command(command)
        filtered_output = self.text_filter.filter(
            command=command, stdout=result.stdout, stderr=result.stderr
        )
        return ProcessedCommandResult(
            filtered_output=filtered_output,
            stderr=result.stderr,
            returncode=result.returncode,
        )

    @classmethod
    def create(cls) -> "ShtymApplication":
        """Factory method to create a ShtymApplication with the appropriate filter.

        Returns:
            An instance of ShtymApplication.
        """
        try:
            filter_module = importlib.import_module("shtym.domain.filter")
            ollama_module = importlib.import_module(
                "shtym.infrastructure.ollama_client"
            )

            llm_client = ollama_module.OllamaLLMClient.create()
            if llm_client.is_available():
                text_filter: Filter = filter_module.LLMFilter(llm_client=llm_client)
            else:
                text_filter = PassThroughFilter()
        except ModuleNotFoundError:
            # Ollama not installed, fall back to PassThroughFilter
            text_filter = PassThroughFilter()
        return cls(text_filter=text_filter)
