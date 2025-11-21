"""Standard I/O handling for shtym."""

import sys


def write_stdout(text: str) -> None:
    """Write text to stdout.

    Args:
        text: The text to write to stdout.
    """
    sys.stdout.write(text)
    sys.stdout.flush()


def write_stderr(text: str) -> None:
    """Write text to stderr.

    Args:
        text: The text to write to stderr.
    """
    sys.stderr.write(text)
    sys.stderr.flush()
