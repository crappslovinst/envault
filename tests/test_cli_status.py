"""Tests for envault/cli_status.py"""

import pytest
from unittest.mock import patch
from envault.cli_status import cmd_status


@pytest.fixture
def mock_status_fns():
    with patch("envault.cli_status.get_status") as mock_get, \
         patch("envault.cli_status.format_status") as mock_fmt:
        mock_get.return_value = {
            "vault": "myapp",
            "locked": False,
            "expired": False,
            "ttl": None,
            "tags": [],
            "last_event": None,
            "event_count": 0,
        }
        mock_fmt.return_value = "Vault   : myapp\nLocked  : no"
        yield {"get": mock_get, "fmt": mock_fmt}


def test_cmd_status_ok(mock_status_fns):
    result = cmd_status("myapp", "pw")
    assert result["ok"] is True
    assert result["status"]["vault"] == "myapp"


def test_cmd_status_includes_formatted_by_default(mock_status_fns):
    result = cmd_status("myapp", "pw", fmt="text")
    assert "formatted" in result
    assert "myapp" in result["formatted"]


def test_cmd_status_raw_skips_formatted(mock_status_fns):
    result = cmd_status("myapp", "pw", fmt="raw")
    assert "formatted" not in result
    assert result["ok"] is True


def test_cmd_status_error_on_missing_vault(mock_status_fns):
    from envault.env_status import StatusError
    mock_status_fns["get"].side_effect = StatusError("Vault 'ghost' does not exist.")
    result = cmd_status("ghost", "pw")
    assert result["ok"] is False
    assert "ghost" in result["error"]


def test_cmd_status_passes_password(mock_status_fns):
    cmd_status("myapp", "secret")
    mock_status_fns["get"].assert_called_once_with("myapp", "secret")
