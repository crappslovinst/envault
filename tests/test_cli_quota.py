import pytest
from unittest.mock import patch
from envault.cli_quota import cmd_quota


@pytest.fixture
def mock_quota_fn(monkeypatch):
    def _quota(vault, password, max_keys=100, max_value_length=1024):
        return {
            "vault": vault,
            "total_keys": 5,
            "max_keys": max_keys,
            "max_value_length": max_value_length,
            "violations": [],
            "ok": True,
        }
    monkeypatch.setattr("envault.cli_quota.check_quota", _quota)
    return monkeypatch


def test_cmd_quota_ok(mock_quota_fn):
    result = cmd_quota("myvault", "pass")
    assert result["ok"] is True
    assert result["vault"] == "myvault"


def test_cmd_quota_includes_formatted_by_default(mock_quota_fn):
    result = cmd_quota("myvault", "pass")
    assert "formatted" in result
    assert isinstance(result["formatted"], str)


def test_cmd_quota_raw_skips_formatted(mock_quota_fn):
    result = cmd_quota("myvault", "pass", raw=True)
    assert "formatted" not in result


def test_cmd_quota_error_on_missing_vault(monkeypatch):
    from envault.env_quota import QuotaError
    monkeypatch.setattr("envault.cli_quota.check_quota", lambda *a, **kw: (_ for _ in ()).throw(QuotaError("not found")))
    result = cmd_quota("ghost", "pass")
    assert result["ok"] is False
    assert "not found" in result["error"]


def test_cmd_quota_passes_limits(monkeypatch):
    calls = {}
    def _quota(vault, password, max_keys=100, max_value_length=1024):
        calls["max_keys"] = max_keys
        calls["max_value_length"] = max_value_length
        return {"vault": vault, "total_keys": 1, "max_keys": max_keys,
                "max_value_length": max_value_length, "violations": [], "ok": True}
    monkeypatch.setattr("envault.cli_quota.check_quota", _quota)
    cmd_quota("v", "p", max_keys=50, max_value_length=256)
    assert calls["max_keys"] == 50
    assert calls["max_value_length"] == 256
