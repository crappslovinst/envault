"""Tests for envault/search.py"""

import pytest
from unittest.mock import patch, MagicMock
from envault.search import search_key, search_value


VAULT_A = {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET_KEY": "abc123"}
VAULT_B = {"API_KEY": "xyz789", "DB_NAME": "mydb", "DEBUG": "true"}


def _make_get_env(mapping: dict):
    """Return a side_effect fn that returns vault data by name."""
    def _get(vault_name, password):
        if vault_name not in mapping:
            raise KeyError(vault_name)
        return mapping[vault_name]
    return _get


@pytest.fixture()
def patched_search():
    with patch("envault.search.list_vaults", return_value=["a", "b"]) as lv, \
         patch("envault.search.get_env_vars", side_effect=_make_get_env({"a": VAULT_A, "b": VAULT_B})) as ge:
        yield lv, ge


def test_search_key_finds_across_vaults(patched_search):
    results = search_key("DB", password="pw")
    keys = [(r["vault"], r["key"]) for r in results]
    assert ("a", "DB_HOST") in keys
    assert ("a", "DB_PORT") in keys
    assert ("b", "DB_NAME") in keys


def test_search_key_case_insensitive_by_default(patched_search):
    results = search_key("db", password="pw")
    assert len(results) == 3


def test_search_key_case_sensitive(patched_search):
    results = search_key("db", password="pw", case_sensitive=True)
    assert results == []


def test_search_key_single_vault(patched_search):
    results = search_key("DB", password="pw", vault_name="a")
    assert all(r["vault"] == "a" for r in results)
    assert len(results) == 2


def test_search_key_no_match(patched_search):
    results = search_key("NONEXISTENT", password="pw")
    assert results == []


def test_search_value_finds_match(patched_search):
    results = search_value("localhost", password="pw")
    assert len(results) == 1
    assert results[0]["key"] == "DB_HOST"
    assert results[0]["vault"] == "a"


def test_search_value_case_insensitive(patched_search):
    results = search_value("TRUE", password="pw")
    assert len(results) == 1
    assert results[0]["key"] == "DEBUG"


def test_search_value_case_sensitive_no_match(patched_search):
    results = search_value("TRUE", password="pw", case_sensitive=True)
    assert results == []


def test_search_skips_inaccessible_vault():
    with patch("envault.search.list_vaults", return_value=["good", "bad"]), \
         patch("envault.search.get_env_vars", side_effect=_make_get_env({"good": VAULT_A})):
        results = search_key("DB", password="pw")
        assert all(r["vault"] == "good" for r in results)


def test_search_empty_vault_list():
    with patch("envault.search.list_vaults", return_value=[]):
        assert search_key("DB", password="pw") == []
        assert search_value("localhost", password="pw") == []
