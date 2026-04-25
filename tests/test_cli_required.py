"""Tests for envault.cli_required."""

import pytest
from unittest.mock import patch

from envault.cli_required import cmd_check_required

VAULT = "myvault"
PASS = "secret"

_OK_RESULT = {
    "vault": VAULT,
    "required": ["DB_HOST"],
    "present": ["DB_HOST"],
    "missing": [],
    "ok": True,
}

_FAIL_RESULT = {
    "vault": VAULT,
    "required": ["DB_HOST", "GHOST"],
    "present": ["DB_HOST"],
    "missing": ["GHOST"],
    "ok": False,
}


@pytest.fixture
def mock_check():
    with patch("envault.cli_required.check_required", return_value=_OK_RESULT) as m:
        yield m


@pytest.fixture
def mock_enforce():
    with patch("envault.cli_required.enforce_required", return_value=_OK_RESULT) as m:
        yield m


def test_cmd_check_required_ok(mock_check):
    result = cmd_check_required(VAULT, PASS, ["DB_HOST"])
    assert result["ok"] is True


def test_cmd_check_required_includes_formatted_by_default(mock_check):
    result = cmd_check_required(VAULT, PASS, ["DB_HOST"])
    assert "formatted" in result


def test_cmd_check_required_raw_skips_formatted(mock_check):
    result = cmd_check_required(VAULT, PASS, ["DB_HOST"], raw=True)
    assert "formatted" not in result


def test_cmd_check_required_calls_enforce_when_flag_set(mock_enforce):
    result = cmd_check_required(VAULT, PASS, ["DB_HOST"], enforce=True)
    mock_enforce.assert_called_once_with(VAULT, PASS, ["DB_HOST"])
    assert result["ok"] is True


def test_cmd_check_required_error_on_missing_vault():
    from envault.env_required import RequiredError
    with patch("envault.cli_required.check_required", side_effect=RequiredError("not found")):
        result = cmd_check_required(VAULT, PASS, ["DB_HOST"])
        assert result["ok"] is False
        assert "not found" in result["error"]


def test_cmd_check_required_enforce_error_propagates_as_ok_false():
    from envault.env_required import RequiredError
    with patch("envault.cli_required.enforce_required",
               side_effect=RequiredError("missing required keys: GHOST")):
        result = cmd_check_required(VAULT, PASS, ["GHOST"], enforce=True)
        assert result["ok"] is False
        assert "GHOST" in result["error"]
