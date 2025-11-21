"""Test suite for shtym CLI."""

from pytest_mock import MockerFixture

from shtym import cli
from shtym.application import ProcessedCommandResult


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
    """Test that main executes a command with 'run' subcommand."""
    mock_process_command = mocker.patch("shtym.cli.process_command")
    mock_process_command.return_value = ProcessedCommandResult(
        filtered_output="test output\n",
        returncode=0,
    )
    mock_write_stdout = mocker.patch("shtym.cli.write_stdout")
    mock_sys_exit = mocker.patch("sys.exit")
    mocker.patch("sys.argv", ["stym", "run", "echo", "test"])

    cli.main()

    # Check that process_command was called with command and a filter
    assert mock_process_command.call_count == 1
    call_args = mock_process_command.call_args
    assert call_args[0][0] == ["echo", "test"]
    mock_write_stdout.assert_called_once_with("test output\n")
    mock_sys_exit.assert_called_once_with(0)
