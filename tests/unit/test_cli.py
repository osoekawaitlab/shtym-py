"""Test suite for shtym CLI."""

from pytest_mock import MockerFixture

from shtym import cli
from shtym.application import ProcessedCommandResult


def test_main_without_subcommand_shows_help(mocker: MockerFixture) -> None:
    """Test that main shows help and exits with 1 when no subcommand provided."""
    mocker.patch("sys.argv", ["stym"])
    mock_sys_exit = mocker.patch("sys.exit")
    mock_parser = mocker.MagicMock()
    mocker.patch("shtym.cli.generate_cli_parser", return_value=mock_parser)
    mock_parser.parse_args.return_value = mocker.MagicMock(subcommand=None)

    cli.main()

    mock_parser.print_help.assert_called_once()
    mock_sys_exit.assert_called_once_with(1)


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
        stderr="",
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


def test_main_propagates_stderr(mocker: MockerFixture) -> None:
    """Test that main propagates stderr from child process."""
    mock_process_command = mocker.patch("shtym.cli.process_command")
    mock_process_command.return_value = ProcessedCommandResult(
        filtered_output="test output\n",
        stderr="error message\n",
        returncode=0,
    )
    mock_write_stdout = mocker.patch("shtym.cli.write_stdout")
    mock_write_stderr = mocker.patch("shtym.cli.write_stderr")
    mock_sys_exit = mocker.patch("sys.exit")
    mocker.patch("sys.argv", ["stym", "run", "python", "-c", "..."])

    cli.main()

    mock_write_stderr.assert_called_once_with("error message\n")
    mock_write_stdout.assert_called_once_with("test output\n")
    mock_sys_exit.assert_called_once_with(0)
