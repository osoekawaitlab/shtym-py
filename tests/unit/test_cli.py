"""Test suite for shtym CLI."""

import subprocess

from pytest_mock import MockerFixture

from shtym import cli


def test_main(mocker: MockerFixture) -> None:
    """Test that the main function can be called without arguments."""
    mocker.patch("sys.argv", ["stym"])
    # Should not raise an exception
    cli.main()


def test_parser_version(mocker: MockerFixture) -> None:
    """Test that the version argument is set correctly."""
    sys_exit = mocker.patch("sys.exit")
    sut = cli.generate_cli_parser()
    sut.parse_args(["--version"])
    sys_exit.assert_called_once_with(0)


def test_main_executes_command_and_outputs_result(mocker: MockerFixture) -> None:
    """Test that main executes a command and outputs its result."""
    mock_run_command = mocker.patch("shtym.cli.run_command")
    mock_run_command.return_value = subprocess.CompletedProcess(
        args=["echo", "test"],
        returncode=0,
        stdout="test output\n",
        stderr="",
    )
    mock_write_stdout = mocker.patch("shtym.cli.write_stdout")
    mock_sys_exit = mocker.patch("sys.exit")
    mocker.patch("sys.argv", ["stym", "echo", "test"])

    cli.main()

    mock_run_command.assert_called_once_with(["echo", "test"])
    mock_write_stdout.assert_called_once_with("test output\n")
    mock_sys_exit.assert_called_once_with(0)
