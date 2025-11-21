"""Application layer for shtym."""

import subprocess


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
