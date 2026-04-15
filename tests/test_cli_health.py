"""Tests for envault/cli_health.py"""

import pytest
from unittest.mock import patch
from envault.cli_health import cmd_health
from envault.env_health import HealthError


_CLEAN_REPORT = {
    "vault": "myvault",
    "ok": True,
    "issues": [],
    "ttl": None,
    "expired": False,
    "lint": {"issue_count": 0},
    "missing_keys": [],
    "key_count": 4,
}

_UNHEALTHY_REPORT = {
    **_CLEAN_REPORT,
    "ok": False,
    "issues": ["vault has expired (TTL exceeded)"],
    "expired": True,
}


@pytest.fixture()
def mock_check():
    with patch("envault.cli_health.check_health") as m, \
         patch("envault.cli_health.format_health_report") as mf:
        mf.return_value = "formatted"
        yield m, mf


def test_cmd_health_ok(mock_check):
    m_check, _ = mock_check
    m_check.return_value = _CLEAN_REPORT
    result = cmd_health("myvault", "pw")
    assert result["ok"] is True
    assert result["error"] is None
    assert result["summary"] == "formatted"


def test_cmd_health_unhealthy(mock_check):
    m_check, _ = mock_check
    m_check.return_value = _UNHEALTHY_REPORT
    result = cmd_health("myvault", "pw")
    assert result["ok"] is False
    assert result["report"]["expired"] is True


def test_cmd_health_vault_not_found(mock_check):
    m_check, _ = mock_check
    m_check.side_effect = HealthError("Vault 'ghost' not found")
    result = cmd_health("ghost", "pw")
    assert result["ok"] is False
    assert "not found" in result["error"]
    assert result["report"] is None


def test_cmd_health_passes_required_keys(mock_check):
    m_check, _ = mock_check
    m_check.return_value = _CLEAN_REPORT
    cmd_health("myvault", "pw", required_keys=["A", "B"])
    m_check.assert_called_once_with("myvault", "pw", required_keys=["A", "B"])


def test_cmd_health_no_required_keys_default(mock_check):
    m_check, _ = mock_check
    m_check.return_value = _CLEAN_REPORT
    cmd_health("myvault", "pw")
    m_check.assert_called_once_with("myvault", "pw", required_keys=None)
