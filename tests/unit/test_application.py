"""Test suite for application layer."""

import subprocess
from unittest.mock import MagicMock

from pytest_mock import MockerFixture

from shtym import application
from shtym.domain.processor import (
    CommandExecution,
    PassThroughProcessor,
    ProcessedCommandResult,
)


def test_run_command_executes_subprocess(mocker: MockerFixture) -> None:
    """Test that run_command executes a subprocess and returns result."""
    mock_run = mocker.patch("subprocess.run")
    mock_run.return_value = subprocess.CompletedProcess(
        args=["echo", "test"],
        returncode=0,
        stdout="test\n",
        stderr="",
    )
    app = application.ShtymApplication(processor=PassThroughProcessor())

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


def test_process_command_applies_processor(mocker: MockerFixture) -> None:
    """Test that process_command applies processor to command output."""
    mock_processor = MagicMock(spec=PassThroughProcessor)
    mock_processor.process.return_value = "processed output\n"
    app = application.ShtymApplication(processor=mock_processor)

    mock_run_command = mocker.patch.object(app, "run_command")
    mock_run_command.return_value = subprocess.CompletedProcess(
        args=["echo", "test"],
        returncode=0,
        stdout="test output\n",
        stderr="",
    )
    expected_execution = CommandExecution(
        command=["echo", "test"], stdout="test output\n", stderr=""
    )
    expected = ProcessedCommandResult(
        processed_output="processed output\n", stderr="", returncode=0
    )

    result = app.process_command(["echo", "test"])

    mock_run_command.assert_called_once_with(["echo", "test"])
    mock_processor.process.assert_called_once_with(expected_execution)
    assert result == expected


def test_process_command_with_passthrough_filter() -> None:
    """Test that process_command with PassThroughProcessor returns original output."""
    app = application.ShtymApplication(processor=PassThroughProcessor())

    result = app.process_command(["echo", "test"])

    assert result.processed_output == "test\n"
    assert result.returncode == 0


def test_process_command_includes_stderr(mocker: MockerFixture) -> None:
    """Test that process_command includes stderr in result."""
    mock_processor = MagicMock(spec=PassThroughProcessor)
    mock_processor.process.return_value = "processed output\n"
    app = application.ShtymApplication(processor=mock_processor)

    mock_run_command = mocker.patch.object(app, "run_command")
    mock_run_command.return_value = subprocess.CompletedProcess(
        args=["python", "-c", "import sys; sys.stderr.write('error')"],
        returncode=0,
        stdout="output\n",
        stderr="error message\n",
    )
    expected = ProcessedCommandResult(
        processed_output="processed output\n", stderr="error message\n", returncode=0
    )

    result = app.process_command(
        ["python", "-c", "import sys; sys.stderr.write('error')"]
    )

    assert result == expected


def test_application_create(mocker: MockerFixture) -> None:
    """Test that ShtymApplication.create initializes with the correct processor."""
    mock_create_processor_from_profile_name = mocker.patch(
        "shtym.application.create_processor_from_profile_name"
    )
    mock_profile_repository_factory = mocker.patch(
        "shtym.application.ProfileRepositoryFactory"
    )
    mock_processor_factory = mocker.patch("shtym.application.ConcreteProcessorFactory")

    actual = application.ShtymApplication.create(profile_name="test-profile")

    assert actual.processor == mock_create_processor_from_profile_name.return_value
    mock_create_processor_from_profile_name.assert_called_once_with(
        profile_name="test-profile",
        profile_repository=mock_profile_repository_factory.return_value.create.return_value,
        processor_factory=mock_processor_factory.return_value,
    )
    mock_profile_repository_factory.assert_called_once_with()
    mock_profile_repository_factory.return_value.create.assert_called_once_with()
