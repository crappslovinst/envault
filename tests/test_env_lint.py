"""Tests for envault/env_lint.py"""

import pytest
from unittest.mock import patch
from envault.env_lint import lint_vault, format_lint_result, LintError


BASE_ENV = {
    "DATABASE_URL": "postgres://localhost/db",
    "SECRET_KEY": "supersecret",
    "DEBUG": "false",
}


@pytest.fixture
def mock_get_env():
    with patch("envault.env_lint.get_env_vars") as m:
        yield m


def test_lint_passes_clean_vault(mock_get_env):
    mock_get_env.return_value = BASE_ENV.copy()
    result = lint_vault("myapp", "pass")
    assert result["passed"] is True
    assert result["total_issues"] == 0


def test_lint_detects_empty_values(mock_get_env):
    mock_get_env.return_value = {"API_KEY": "", "HOST": "localhost"}
    result = lint_vault("myapp", "pass")
    assert result["passed"] is False
    assert any(f["key"] == "API_KEY" for f in result["findings"]["empty_values"])


def test_lint_detects_keys_not_uppercase(mock_get_env):
    mock_get_env.return_value = {"api_key": "abc", "HOST": "localhost"}
    result = lint_vault("myapp", "pass")
    issues = result["findings"]["keys_not_uppercase"]
    assert any(f["key"] == "api_key" for f in issues)
    assert issues[0]["suggested"] == "API_KEY"


def test_lint_detects_suspicious_placeholders(mock_get_env):
    mock_get_env.return_value = {"SECRET": "CHANGEME", "HOST": "localhost"}
    result = lint_vault("myapp", "pass")
    issues = result["findings"]["suspicious_placeholders"]
    assert any(f["key"] == "SECRET" for f in issues)


def test_lint_detects_whitespace_in_keys(mock_get_env):
    mock_get_env.return_value = {" BAD_KEY": "value"}
    result = lint_vault("myapp", "pass")
    assert len(result["findings"]["whitespace_in_keys"]) == 1


def test_lint_respects_rule_filter(mock_get_env):
    mock_get_env.return_value = {"api_key": "", "HOST": "ok"}
    result = lint_vault("myapp", "pass", rules=["empty_values"])
    assert "empty_values" in result["findings"]
    assert "keys_not_uppercase" not in result["findings"]


def test_lint_raises_on_bad_vault(mock_get_env):
    mock_get_env.side_effect = Exception("vault not found")
    with pytest.raises(LintError, match="vault not found"):
        lint_vault("missing", "pass")


def test_format_lint_result_passed(mock_get_env):
    mock_get_env.return_value = BASE_ENV.copy()
    result = lint_vault("myapp", "pass")
    formatted = format_lint_result(result)
    assert "No issues found" in formatted


def test_format_lint_result_with_issues(mock_get_env):
    mock_get_env.return_value = {"api_key": "CHANGEME"}
    result = lint_vault("myapp", "pass")
    formatted = format_lint_result(result)
    assert "keys_not_uppercase" in formatted or "suspicious_placeholders" in formatted
    assert "Total issues" in formatted


def test_lint_vault_name_in_result(mock_get_env):
    mock_get_env.return_value = BASE_ENV.copy()
    result = lint_vault("staging", "pass")
    assert result["vault"] == "staging"
