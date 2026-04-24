"""Tests for envault/env_tokenize.py."""

import pytest
from unittest.mock import patch
from envault.env_tokenize import (
    TokenizeError,
    _split_token,
    tokenize_vault,
    get_token_roots,
    group_by_root,
    format_tokenize_result,
)

SAMPLE_ENV = {
    "APP_DB_HOST": "localhost",
    "APP_DB_PORT": "5432",
    "APP_SECRET_KEY": "abc",
    "REDIS_URL": "redis://localhost",
}


@pytest.fixture
def mock_get_env():
    with patch("envault.env_tokenize.get_env_vars", return_value=SAMPLE_ENV) as m:
        yield m


def test_split_token_basic():
    assert _split_token("APP_DB_HOST") == ["APP", "DB", "HOST"]


def test_split_token_custom_delimiter():
    assert _split_token("app.db.host", ".") == ["app", "db", "host"]


def test_split_token_single_segment():
    assert _split_token("SIMPLE") == ["SIMPLE"]


def test_tokenize_vault_returns_all_keys(mock_get_env):
    result = tokenize_vault("myvault", "pass")
    assert set(result.keys()) == set(SAMPLE_ENV.keys())


def test_tokenize_vault_depth_correct(mock_get_env):
    result = tokenize_vault("myvault", "pass")
    assert result["APP_DB_HOST"]["depth"] == 3
    assert result["REDIS_URL"]["depth"] == 2


def test_tokenize_vault_root_and_leaf(mock_get_env):
    result = tokenize_vault("myvault", "pass")
    assert result["APP_DB_HOST"]["root"] == "APP"
    assert result["APP_DB_HOST"]["leaf"] == "HOST"


def test_tokenize_vault_prefix_filter(mock_get_env):
    result = tokenize_vault("myvault", "pass", prefix_filter="APP")
    assert all(k.startswith("APP") for k in result)
    assert "REDIS_URL" not in result


def test_tokenize_vault_raises_on_error():
    with patch("envault.env_tokenize.get_env_vars", side_effect=Exception("bad")):
        with pytest.raises(TokenizeError, match="bad"):
            tokenize_vault("missing", "pass")


def test_tokenize_vault_raises_on_empty():
    with patch("envault.env_tokenize.get_env_vars", return_value={}):
        with pytest.raises(TokenizeError, match="empty"):
            tokenize_vault("empty", "pass")


def test_get_token_roots(mock_get_env):
    tokenized = tokenize_vault("myvault", "pass")
    roots = get_token_roots(tokenized)
    assert "APP" in roots
    assert "REDIS" in roots


def test_group_by_root(mock_get_env):
    tokenized = tokenize_vault("myvault", "pass")
    grouped = group_by_root(tokenized)
    assert "APP" in grouped
    assert "APP_DB_HOST" in grouped["APP"]
    assert "REDIS" in grouped


def test_format_tokenize_result_non_empty(mock_get_env):
    tokenized = tokenize_vault("myvault", "pass")
    out = format_tokenize_result(tokenized)
    assert "Tokenized keys" in out
    assert "APP_DB_HOST" in out


def test_format_tokenize_result_empty():
    out = format_tokenize_result({})
    assert "No keys" in out
