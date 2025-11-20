"""Unit tests for shtym exports."""

import re

import shtym


def test_shtym_exports_version() -> None:
    """Test that shtym exports the correct version."""
    assert re.match(r"^\d+\.\d+\.\d+$", shtym.__version__)
