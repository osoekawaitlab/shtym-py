"""Application layer for shtym."""

import subprocess
from dataclasses import dataclass

from shtym.domain.filter import Filter


@dataclass
class ProcessedCommandResult:
    """Result of processing a command with a filter."""

    filtered_output: str
    returncode: int


def run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    """Execute a command as a subprocess.

    Args:
        command: The command and its arguments as a list.

    Returns:
        The completed process result.
    """
    return subprocess.run(  # noqa: S603
        command, capture_output=True, text=True, check=False
    )


def process_command(command: list[str], text_filter: Filter) -> ProcessedCommandResult:
    """Execute a command and apply a filter to its output.

    Args:
        command: The command and its arguments as a list.
        text_filter: The filter to apply to the command output.

    Returns:
        The processed command result with filtered output and return code.
    """
    result = run_command(command)
    filtered_output = text_filter.filter(result.stdout)
    return ProcessedCommandResult(
        filtered_output=filtered_output,
        returncode=result.returncode,
    )
