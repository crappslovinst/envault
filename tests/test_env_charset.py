import pytest
from unittest.mock import patch
from envault.env_charset import analyze_charset, format_charset_result, CharsetError


def _make_get_env(data):
    return lambda vault, password: data


@pytest.fixture
def mock_charset_deps(monkeypatch):
    def _patch(exists_result, env_data):
        monkeypatch.setattr("envault.env_charset.vault_exists", lambda v: exists_result)
        monkeypatch.setattr("envault.env_charset.get_env_vars", _make_get_env(env_data))
    return _patch


def test_analyze_raises_if_vault_missing(mock_charset_deps):
    mock_charset_deps(False, {})
    with pytest.raises(CharsetError, match="not found"):
        analyze_charset("ghost", "pw")


def test_analyze_clean_vault(mock_charset_deps):
    mock_charset_deps(True, {"HOST": "localhost", "PORT": "8080"})
    result = analyze_charset("myenv", "pw")
    assert result["flagged_count"] == 0
    assert result["clean_count"] == 2
    assert result["total"] == 2


def test_analyze_detects_non_ascii(mock_charset_deps):
    mock_charset_deps(True, {"NAME": "caf\u00e9", "HOST": "localhost"})
    result = analyze_charset("myenv", "pw", flag_non_ascii=True)
    keys = [e["key"] for e in result["flagged"]]
    assert "NAME" in keys
    assert "HOST" not in keys


def test_analyze_skips_non_ascii_when_disabled(mock_charset_deps):
    mock_charset_deps(True, {"NAME": "caf\u00e9"})
    result = analyze_charset("myenv", "pw", flag_non_ascii=False)
    assert result["flagged_count"] == 0


def test_analyze_detects_control_chars(mock_charset_deps):
    mock_charset_deps(True, {"BAD": "hello\x00world", "OK": "fine"})
    result = analyze_charset("myenv", "pw", flag_control=True)
    keys = [e["key"] for e in result["flagged"]]
    assert "BAD" in keys
    assert "OK" not in keys


def test_analyze_detects_whitespace_only(mock_charset_deps):
    mock_charset_deps(True, {"BLANK": "   ", "REAL": "value"})
    result = analyze_charset("myenv", "pw")
    keys = [e["key"] for e in result["flagged"]]
    assert "BLANK" in keys


def test_flagged_entry_has_reasons(mock_charset_deps):
    mock_charset_deps(True, {"X": "\u00e9"})
    result = analyze_charset("myenv", "pw")
    assert result["flagged"][0]["reasons"] == ["non_ascii"]


def test_format_charset_result_includes_vault_name(mock_charset_deps):
    mock_charset_deps(True, {"A": "ok"})
    result = analyze_charset("prod", "pw")
    formatted = format_charset_result(result)
    assert "prod" in formatted
    assert "Total" in formatted
    assert "Clean" in formatted


def test_format_charset_result_lists_flagged_keys(mock_charset_deps):
    mock_charset_deps(True, {"BAD": "   ", "OK": "fine"})
    result = analyze_charset("env", "pw")
    formatted = format_charset_result(result)
    assert "BAD" in formatted
    assert "whitespace_only" in formatted
