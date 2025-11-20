"""CLI module for shtym."""

from argparse import ArgumentParser

from shtym.core import __version__


def generate_cli_parser() -> ArgumentParser:
    """Generate the argument parser for the shtym CLI."""
    parser = ArgumentParser(
        description="shtym: AI-powered summary filter "
        "that distills any command's output."
    )
    parser.add_argument("--version", action="version", version=__version__)
    return parser


def main() -> None:
    """Entry point for the shtym command-line interface."""
    parser = generate_cli_parser()
    _ = parser.parse_args()
