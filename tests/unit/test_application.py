"""Test suite for application layer."""

import subprocess

from pytest_mock import MockerFixture

from shtym import application
from shtym.domain.filter import PassThroughFilter


def test_run_command_executes_subprocess(mocker: MockerFixture) -> None:
    """Test that run_command executes a subprocess and returns result."""
    mock_run = mocker.patch("subprocess.run")
    mock_run.return_value = subprocess.CompletedProcess(
        args=["echo", "test"],
        returncode=0,
        stdout="test\n",
        stderr="",
    )
    app = application.ShtymApplication(text_filter=PassThroughFilter())

    result = app.run_command(["echo", "test"])

    mock_run.assert_called_once_with(
        ["echo", "test"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert result.stdout == "test\n"
    assert result.stderr == ""


def test_process_command_applies_filter(mocker: MockerFixture) -> None:
    """Test that process_command applies filter to command output."""
    mock_filter = mocker.Mock(spec=PassThroughFilter)
    mock_filter.filter.return_value = "filtered output\n"
    app = application.ShtymApplication(text_filter=mock_filter)

    mock_run_command = mocker.patch.object(app, "run_command")
    mock_run_command.return_value = subprocess.CompletedProcess(
        args=["echo", "test"],
        returncode=0,
        stdout="test output\n",
        stderr="",
    )

    result = app.process_command(["echo", "test"])

    mock_run_command.assert_called_once_with(["echo", "test"])
    mock_filter.filter.assert_called_once_with(
        command=["echo", "test"], stdout="test output\n", stderr=""
    )
    assert result.filtered_output == "filtered output\n"
    assert result.stderr == ""
    assert result.returncode == 0


def test_process_command_with_passthrough_filter() -> None:
    """Test that process_command with PassThroughFilter returns original output."""
    app = application.ShtymApplication(text_filter=PassThroughFilter())

    result = app.process_command(["echo", "test"])

    assert result.filtered_output == "test\n"
    assert result.returncode == 0


def test_process_command_includes_stderr(mocker: MockerFixture) -> None:
    """Test that process_command includes stderr in result."""
    mock_filter = mocker.Mock(spec=PassThroughFilter)
    mock_filter.filter.return_value = "filtered output\n"
    app = application.ShtymApplication(text_filter=mock_filter)

    mock_run_command = mocker.patch.object(app, "run_command")
    mock_run_command.return_value = subprocess.CompletedProcess(
        args=["python", "-c", "import sys; sys.stderr.write('error')"],
        returncode=0,
        stdout="output\n",
        stderr="error message\n",
    )

    result = app.process_command(
        ["python", "-c", "import sys; sys.stderr.write('error')"]
    )

    assert result.stderr == "error message\n"
    assert result.filtered_output == "filtered output\n"
    assert result.returncode == 0
