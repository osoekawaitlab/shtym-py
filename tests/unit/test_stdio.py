"""Test suite for stdio infrastructure."""

from io import StringIO

from pytest_mock import MockerFixture

from shtym.infrastructure import stdio


def test_write_stdout_writes_to_stdout(mocker: MockerFixture) -> None:
    """Test that write_stdout writes to sys.stdout."""
    mock_stdout = StringIO()
    mocker.patch("sys.stdout", mock_stdout)

    stdio.write_stdout("output text\n")

    assert mock_stdout.getvalue() == "output text\n"
