"""Tests for envault.env_summarize."""

import pytest
from unittest.mock import patch

from envault.env_summarize import SummarizeError, summarize_vault, format_summary


SAMPLE_ENV = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "DB_PASSWORD": "secret",
    "APP_NAME": "myapp",
    "APP_SECRET_KEY": "abc123",
    "EMPTY_VAR": "",
    "PLAIN": "value",
}


@pytest.fixture
def mock_get_env():
    with patch("envault.env_summarize.get_env_vars", return_value=SAMPLE_ENV) as m:
        yield m


def test_summarize_total(mock_get_env):
    result = summarize_vault("myvault", "pw")
    assert result["total"] == len(SAMPLE_ENV)


def test_summarize_empty_count(mock_get_env):
    result = summarize_vault("myvault", "pw")
    assert result["empty"] == 1


def test_summarize_non_empty_count(mock_get_env):
    result = summarize_vault("myvault", "pw")
    assert result["non_empty"] == result["total"] - result["empty"]


def test_summarize_sensitive_count(mock_get_env):
    result = summarize_vault("myvault", "pw")
    # DB_PASSWORD and APP_SECRET_KEY should be flagged
    assert result["sensitive"] >= 2


def test_summarize_top_prefixes(mock_get_env):
    result = summarize_vault("myvault", "pw")
    prefixes = result["top_prefixes"]
    assert "DB" in prefixes
    assert "APP" in prefixes
    assert prefixes["DB"] == 3
    assert prefixes["APP"] == 2


def test_summarize_vault_name_in_result(mock_get_env):
    result = summarize_vault("myvault", "pw")
    assert result["vault"] == "myvault"


def test_summarize_raises_on_bad_vault():
    with patch(
        "envault.env_summarize.get_env_vars",
        side_effect=Exception("not found"),
    ):
        with pytest.raises(SummarizeError, match="not found"):
            summarize_vault("missing", "pw")


def test_format_summary_contains_vault_name(mock_get_env):
    result = summarize_vault("myvault", "pw")
    formatted = format_summary(result)
    assert "myvault" in formatted


def test_format_summary_contains_counts(mock_get_env):
    result = summarize_vault("myvault", "pw")
    formatted = format_summary(result)
    assert str(result["total"]) in formatted
    assert str(result["empty"]) in formatted


def test_format_summary_shows_prefixes(mock_get_env):
    result = summarize_vault("myvault", "pw")
    formatted = format_summary(result)
    assert "DB" in formatted
    assert "APP" in formatted


def test_format_summary_no_prefixes():
    result = {
        "vault": "v",
        "total": 1,
        "empty": 0,
        "non_empty": 1,
        "sensitive": 0,
        "top_prefixes": {},
    }
    formatted = format_summary(result)
    assert "Top prefix" not in formatted
