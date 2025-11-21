"""CLI module for shtym."""

import argparse
import sys

from shtym._version import __version__
from shtym.application import run_command
from shtym.infrastructure.stdio import write_stdout


def generate_cli_parser() -> argparse.ArgumentParser:
    """Generate the argument parser for the shtym CLI."""
    parser = argparse.ArgumentParser(
        description="shtym: AI-powered summary filter "
        "that distills any command's output."
    )
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help="Command to execute and filter output",
    )
    return parser


def main() -> None:
    """Entry point for the shtym command-line interface."""
    parser = generate_cli_parser()
    args = parser.parse_args()

    if args.command:
        result = run_command(args.command)
        write_stdout(result.stdout)
        sys.exit(result.returncode)
