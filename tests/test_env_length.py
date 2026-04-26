"""Tests for envault.env_length."""

import pytest
from unittest.mock import patch

from envault.env_length import analyze_lengths, check_length_limits, format_length_result, LengthError


ENV = {
    "SHORT": "hi",
    "MEDIUM": "hello world",
    "LONG": "a" * 50,
    "EMPTY": "",
}


@pytest.fixture()
def mock_deps(monkeypatch):
    monkeypatch.setattr("envault.env_length.vault_exists", lambda name: True)
    monkeypatch.setattr("envault.env_length.get_env_vars", lambda name, pw: dict(ENV))


def test_analyze_lengths_total(mock_deps):
    result = analyze_lengths("myvault", "pass")
    assert result["total"] == 4


def test_analyze_lengths_min_is_zero(mock_deps):
    result = analyze_lengths("myvault", "pass")
    assert result["min"] == 0


def test_analyze_lengths_max(mock_deps):
    result = analyze_lengths("myvault", "pass")
    assert result["max"] == 50


def test_analyze_lengths_entries_sorted_desc(mock_deps):
    result = analyze_lengths("myvault", "pass")
    lengths = [e["length"] for e in result["entries"]]
    assert lengths == sorted(lengths, reverse=True)


def test_analyze_lengths_raises_if_vault_missing(monkeypatch):
    monkeypatch.setattr("envault.env_length.vault_exists", lambda name: False)
    with pytest.raises(LengthError, match="not found"):
        analyze_lengths("ghost", "pass")


def test_analyze_lengths_empty_vault(monkeypatch):
    monkeypatch.setattr("envault.env_length.vault_exists", lambda name: True)
    monkeypatch.setattr("envault.env_length.get_env_vars", lambda name, pw: {})
    result = analyze_lengths("empty", "pass")
    assert result["total"] == 0
    assert result["min"] is None


def test_check_length_limits_no_violations(mock_deps):
    result = check_length_limits("myvault", "pass", max_length=100)
    assert result["ok"] is True
    assert result["violations"] == []


def test_check_length_limits_detects_above_max(mock_deps):
    result = check_length_limits("myvault", "pass", max_length=10)
    keys = [v["key"] for v in result["violations"]]
    assert "LONG" in keys
    assert "MEDIUM" in keys


def test_check_length_limits_detects_below_min(mock_deps):
    result = check_length_limits("myvault", "pass", min_length=3)
    keys = [v["key"] for v in result["violations"]]
    assert "SHORT" in keys
    assert "EMPTY" in keys


def test_check_length_limits_raises_on_bad_range(mock_deps):
    with pytest.raises(LengthError, match="cannot exceed"):
        check_length_limits("myvault", "pass", min_length=50, max_length=10)


def test_check_length_limits_raises_on_negative(mock_deps):
    with pytest.raises(LengthError, match="non-negative"):
        check_length_limits("myvault", "pass", min_length=-1)


def test_format_length_result_ok():
    result = {
        "vault": "myvault",
        "checked": 4,
        "violations": [],
        "ok": True,
    }
    out = format_length_result(result)
    assert "All values within length limits" in out


def test_format_length_result_violations():
    result = {
        "vault": "myvault",
        "checked": 4,
        "violations": [{"key": "LONG", "length": 50, "reason": "above max (10)"}],
        "ok": False,
    }
    out = format_length_result(result)
    assert "LONG" in out
    assert "above max" in out
