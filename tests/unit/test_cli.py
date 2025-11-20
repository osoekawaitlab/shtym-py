"""Test suite for shtym CLI."""

from pytest_mock import MockerFixture

from shtym import cli


def test_main(mocker: MockerFixture) -> None:
    """Test that the main function can be called."""
    generate_cli_parser = mocker.patch("shtym.cli.generate_cli_parser")
    cli.main()
    generate_cli_parser.assert_called_once_with()


def test_parser_version(mocker: MockerFixture) -> None:
    """Test that the version argument is set correctly."""
    sys_exit = mocker.patch("sys.exit")
    sut = cli.generate_cli_parser()
    sut.parse_args(["--version"])
    sys_exit.assert_called_once_with(0)
