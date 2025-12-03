"""Fixtures for tests."""

nox_pytest_failure_message = r"""nox > Running session tests_all_versions-3.11
nox > Creating virtual environment (uv) using python3.11 in .nox/tests_all_versions-3-11
nox > /home/nobody/.pyenv/versions/3.12.11/bin/uv pip install -e . --group=dev
nox > pytest 
================================================================================== test session starts ===================================================================================
platform linux -- Python 3.11.13, pytest-9.0.1, pluggy-1.6.0
Using --randomly-seed=3403480798
rootdir: /home/nobody/Documents/works/oitl/shtym-py
configfile: pyproject.toml
testpaths: tests, src
plugins: randomly-4.0.1, mock-3.15.1, cov-7.0.0
collected 10 items                                                                                                                                                                       

tests/unit/test_application.py .                                                                                                                                                   [ 10%]
tests/unit/test_shtym.py .                                                                                                                                                         [ 20%]
tests/unit/test_cli.py ...                                                                                                                                                         [ 50%]
tests/e2e/test_shtym.py ...                                                                                                                                                        [ 80%]
tests/unit/test_stdio.py .F                                                                                                                                                        [100%]

======================================================================================== FAILURES ========================================================================================
___________________________________________________________________________ test_read_stdin_returns_input_text ___________________________________________________________________________

mocker = <pytest_mock.plugin.MockerFixture object at 0x7929840312d0>

    def test_read_stdin_returns_input_text(mocker: MockerFixture) -> None:
        \"\"\"Test that read_stdin reads from sys.stdin.\"\"\"
        mock_stdin = StringIO("test input\n")
        mocker.patch("sys.stdin", mock_stdin)
    
>       result = stdio.read_stdin()
                 ^^^^^^^^^^^^^^^^
E       AttributeError: module 'shtym.infrastructure.stdio' has no attribute 'read_stdin'

tests/unit/test_stdio.py:15: AttributeError
================================================================================ short test summary info =================================================================================
FAILED tests/unit/test_stdio.py::test_read_stdin_returns_input_text - AttributeError: module 'shtym.infrastructure.stdio' has no attribute 'read_stdin'
============================================================================== 1 failed, 9 passed in 0.14s ===============================================================================
nox > Command pytest  failed with exit code 1
nox > Session tests_all_versions-3.11 failed.
"""  # noqa: E501, W291, W293
