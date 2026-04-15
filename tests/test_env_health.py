"""Tests for envault/env_health.py"""

import pytest
from unittest.mock import patch, MagicMock
from envault.env_health import check_health, format_health_report, HealthError


ENV_VARS = {"DB_HOST": "localhost", "API_KEY": "secret", "DEBUG": "true"}


@pytest.fixture()
def mock_health_deps():
    with patch("envault.env_health.vault_exists") as m_exists, \
         patch("envault.env_health.get_env_vars") as m_get, \
         patch("envault.env_health.get_ttl") as m_ttl, \
         patch("envault.env_health.is_expired") as m_exp, \
         patch("envault.env_health.lint_vault") as m_lint:
        m_exists.return_value = True
        m_get.return_value = dict(ENV_VARS)
        m_ttl.return_value = None
        m_exp.return_value = False
        m_lint.return_value = {"issue_count": 0, "issues": []}
        yield {
            "exists": m_exists, "get": m_get, "ttl": m_ttl,
            "expired": m_exp, "lint": m_lint,
        }


def test_check_health_raises_if_vault_missing():
    with patch("envault.env_health.vault_exists", return_value=False):
        with pytest.raises(HealthError, match="not found"):
            check_health("ghost", "pw")


def test_check_health_ok_clean_vault(mock_health_deps):
    result = check_health("myvault", "pw")
    assert result["ok"] is True
    assert result["issues"] == []
    assert result["key_count"] == 3


def test_check_health_reports_expired_ttl(mock_health_deps):
    mock_health_deps["ttl"].return_value = {"expires_at": "2020-01-01T00:00:00"}
    mock_health_deps["expired"].return_value = True
    result = check_health("myvault", "pw")
    assert result["ok"] is False
    assert result["expired"] is True
    assert any("expired" in i for i in result["issues"])


def test_check_health_reports_lint_issues(mock_health_deps):
    mock_health_deps["lint"].return_value = {
        "issue_count": 2,
        "issues": [{"key": "debug", "type": "not_uppercase"}],
    }
    result = check_health("myvault", "pw")
    assert result["ok"] is False
    assert any("lint" in i for i in result["issues"])


def test_check_health_reports_missing_required_keys(mock_health_deps):
    result = check_health("myvault", "pw", required_keys=["DB_HOST", "MISSING_KEY"])
    assert result["ok"] is False
    assert "MISSING_KEY" in result["missing_keys"]
    assert "DB_HOST" not in result["missing_keys"]


def test_check_health_all_required_keys_present(mock_health_deps):
    result = check_health("myvault", "pw", required_keys=["DB_HOST", "API_KEY"])
    assert result["ok"] is True
    assert result["missing_keys"] == []


def test_format_health_report_ok(mock_health_deps):
    report = check_health("myvault", "pw")
    text = format_health_report(report)
    assert "OK" in text
    assert "myvault" in text
    assert "3" in text


def test_format_health_report_unhealthy(mock_health_deps):
    mock_health_deps["lint"].return_value = {"issue_count": 1, "issues": [{}]}
    report = check_health("myvault", "pw")
    text = format_health_report(report)
    assert "UNHEALTHY" in text


def test_check_health_ttl_info_stored(mock_health_deps):
    ttl_data = {"expires_at": "2099-12-31T00:00:00"}
    mock_health_deps["ttl"].return_value = ttl_data
    mock_health_deps["expired"].return_value = False
    result = check_health("myvault", "pw")
    assert result["ttl"] == ttl_data
    assert result["expired"] is False
    assert result["ok"] is True
