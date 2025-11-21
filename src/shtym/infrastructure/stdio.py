"""Standard I/O handling for shtym."""

import sys


def write_stdout(text: str) -> None:
    """Write text to stdout.

    Args:
        text: The text to write to stdout.
    """
    sys.stdout.write(text)
