"""CLI module for shtym."""

import argparse
import sys

from shtym._version import __version__
from shtym.application import process_command
from shtym.domain.filter import PassThroughFilter
from shtym.infrastructure.stdio import write_stdout


def generate_cli_parser() -> argparse.ArgumentParser:
    """Generate the argument parser for the shtym CLI."""
    parser = argparse.ArgumentParser(
        description="shtym: AI-powered summary filter "
        "that distills any command's output."
    )
    parser.add_argument("--version", action="version", version=__version__)

    # Create subparsers for subcommands
    subparsers = parser.add_subparsers(dest="subcommand", help="Available subcommands")

    # 'run' subcommand
    run_parser = subparsers.add_parser(
        "run", help="Execute a command and filter its output"
    )
    run_parser.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help="Command to execute and filter output",
    )

    return parser


def main() -> None:
    """Entry point for the shtym command-line interface."""
    parser = generate_cli_parser()
    args = parser.parse_args()

    if args.subcommand == "run" and args.command:
        text_filter = PassThroughFilter()
        result = process_command(args.command, text_filter)
        write_stdout(result.filtered_output)
        sys.exit(result.returncode)
