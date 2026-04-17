import pytest
from unittest.mock import patch
from envault.env_quota import check_quota, format_quota_result, QuotaError


def _make_get_env(env: dict):
    return lambda vault, password: env


@pytest.fixture
def mock_quota_deps(monkeypatch):
    def _exists(name):
        return True

    monkeypatch.setattr("envault.env_quota.vault_exists", _exists)
    return monkeypatch


def test_check_quota_ok(mock_quota_deps, monkeypatch):
    env = {f"KEY_{i}": "value" for i in range(5)}
    monkeypatch.setattr("envault.env_quota.get_env_vars", _make_get_env(env))
    result = check_quota("myvault", "pass")
    assert result["ok"] is True
    assert result["total_keys"] == 5
    assert result["violations"] == []


def test_check_quota_too_many_keys(mock_quota_deps, monkeypatch):
    env = {f"KEY_{i}": "v" for i in range(10)}
    monkeypatch.setattr("envault.env_quota.get_env_vars", _make_get_env(env))
    result = check_quota("myvault", "pass", max_keys=5)
    assert result["ok"] is False
    types = [v["type"] for v in result["violations"]]
    assert "too_many_keys" in types


def test_check_quota_value_too_long(mock_quota_deps, monkeypatch):
    env = {"SHORT": "hi", "LONG_KEY": "x" * 200}
    monkeypatch.setattr("envault.env_quota.get_env_vars", _make_get_env(env))
    result = check_quota("myvault", "pass", max_value_length=100)
    assert result["ok"] is False
    types = [v["type"] for v in result["violations"]]
    assert "value_too_long" in types


def test_check_quota_multiple_violations(mock_quota_deps, monkeypatch):
    env = {f"KEY_{i}": "x" * 500 for i in range(10)}
    monkeypatch.setattr("envault.env_quota.get_env_vars", _make_get_env(env))
    result = check_quota("myvault", "pass", max_keys=3, max_value_length=100)
    assert result["ok"] is False
    assert len(result["violations"]) > 1


def test_check_quota_raises_if_vault_missing(monkeypatch):
    monkeypatch.setattr("envault.env_quota.vault_exists", lambda name: False)
    with pytest.raises(QuotaError, match="not found"):
        check_quota("ghost", "pass")


def test_format_quota_result_ok():
    result = {
        "vault": "myvault",
        "total_keys": 3,
        "max_keys": 100,
        "max_value_length": 1024,
        "violations": [],
        "ok": True,
    }
    out = format_quota_result(result)
    assert "OK" in out
    assert "myvault" in out


def test_format_quota_result_exceeded():
    result = {
        "vault": "myvault",
        "total_keys": 120,
        "max_keys": 100,
        "max_value_length": 1024,
        "violations": [{"type": "too_many_keys", "detail": "120 keys exceeds limit of 100"}],
        "ok": False,
    }
    out = format_quota_result(result)
    assert "EXCEEDED" in out
    assert "too_many_keys" in out
