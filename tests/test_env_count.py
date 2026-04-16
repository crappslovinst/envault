"""Tests for envault.env_count."""

import pytest
from unittest.mock import patch

from envault.env_count import CountError, count_keys, format_count_result


ENV_DATA = {
    "APP_HOST": "localhost",
    "APP_PORT": "8080",
    "DB_HOST": "db.local",
    "DB_PASS": "",
    "SECRET_KEY": "abc123",
}


@pytest.fixture
def mock_get_env():
    with patch("envault.env_count.get_env_vars", return_value=ENV_DATA) as m:
        yield m


def test_count_total(mock_get_env):
    result = count_keys("myvault", "pass")
    assert result["total"] == 5


def test_count_empty(mock_get_env):
    result = count_keys("myvault", "pass")
    assert result["empty"] == 1


def test_count_non_empty(mock_get_env):
    result = count_keys("myvault", "pass")
    assert result["non_empty"] == 4


def test_count_prefixes(mock_get_env):
    result = count_keys("myvault", "pass")
    assert result["prefixes"]["APP"] == 2
    assert result["prefixes"]["DB"] == 2
    assert result["prefixes"]["SECRET"] == 1


def test_count_vault_name(mock_get_env):
    result = count_keys("myvault", "pass")
    assert result["vault"] == "myvault"


def test_count_raises_on_bad_vault():
    with patch("envault.env_count.get_env_vars", side_effect=Exception("not found")):
        with pytest.raises(CountError, match="not found"):
            count_keys("missing", "pass")


def test_format_count_result(mock_get_env):
    result = count_keys("myvault", "pass")
    formatted = format_count_result(result)
    assert "Total" in formatted
    assert "Empty" in formatted
    assert "APP" in formatted


def test_count_empty_vault():
    with patch("envault.env_count.get_env_vars", return_value={}):
        result = count_keys("empty", "pass")
        assert result["total"] == 0
        assert result["empty"] == 0
        assert result["prefixes"] == {}
