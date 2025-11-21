"""Test suite for application layer."""

import subprocess

from pytest_mock import MockerFixture

from shtym import application


def test_run_command_executes_subprocess(mocker: MockerFixture) -> None:
    """Test that run_command executes a subprocess and returns result."""
    mock_run = mocker.patch("subprocess.run")
    mock_run.return_value = subprocess.CompletedProcess(
        args=["echo", "test"],
        returncode=0,
        stdout="test\n",
        stderr="",
    )

    result = application.run_command(["echo", "test"])

    mock_run.assert_called_once_with(
        ["echo", "test"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert result.stdout == "test\n"
    assert result.stderr == ""
