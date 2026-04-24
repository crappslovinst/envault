"""Tests for env_diff_keys and cli_diff_keys."""

import pytest
from unittest.mock import patch

from envault.env_diff_keys import DiffKeysError, diff_keys, format_diff_keys_result
from envault.cli_diff_keys import cmd_diff_keys


ENV_A = {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "abc"}
ENV_B = {"DB_HOST": "remotehost", "API_KEY": "xyz", "SECRET": "def"}


@pytest.fixture
def patched_get_env():
    with patch("envault.env_diff_keys.get_env_vars") as mock:
        def _side(vault, _pw):
            return {"a": ENV_A, "b": ENV_B}[vault]
        mock.side_effect = _side
        yield mock


def test_diff_keys_only_in_a(patched_get_env):
    result = diff_keys("a", "pw", "b", "pw")
    assert "DB_PORT" in result["only_in_a"]


def test_diff_keys_only_in_b(patched_get_env):
    result = diff_keys("a", "pw", "b", "pw")
    assert "API_KEY" in result["only_in_b"]


def test_diff_keys_in_both(patched_get_env):
    result = diff_keys("a", "pw", "b", "pw")
    assert "DB_HOST" in result["in_both"]
    assert "SECRET" in result["in_both"]


def test_diff_keys_counts(patched_get_env):
    result = diff_keys("a", "pw", "b", "pw")
    assert result["shared"] == 2
    assert result["unique_to_a"] == 1
    assert result["unique_to_b"] == 1
    assert result["total_a"] == 3
    assert result["total_b"] == 3


def test_diff_keys_sorted_output(patched_get_env):
    result = diff_keys("a", "pw", "b", "pw")
    assert result["only_in_a"] == sorted(result["only_in_a"])
    assert result["only_in_b"] == sorted(result["only_in_b"])
    assert result["in_both"] == sorted(result["in_both"])


def test_diff_keys_raises_on_bad_vault_a():
    with patch("envault.env_diff_keys.get_env_vars", side_effect=Exception("not found")):
        with pytest.raises(DiffKeysError, match="vault_a_missing"):
            diff_keys("vault_a_missing", "pw", "b", "pw")


def test_diff_keys_raises_on_bad_vault_b():
    def _side(vault, _pw):
        if vault == "a":
            return ENV_A
        raise Exception("not found")

    with patch("envault.env_diff_keys.get_env_vars", side_effect=_side):
        with pytest.raises(DiffKeysError, match="vault_b_missing"):
            diff_keys("a", "pw", "vault_b_missing", "pw")


def test_format_diff_keys_result(patched_get_env):
    result = diff_keys("a", "pw", "b", "pw")
    formatted = format_diff_keys_result(result)
    assert "Shared keys" in formatted
    assert "Only in A" in formatted
    assert "Only in B" in formatted


def test_cmd_diff_keys_includes_formatted(patched_get_env):
    result = cmd_diff_keys("a", "pw", "b", "pw")
    assert "formatted" in result
    assert "Key diff" in result["formatted"]


def test_cmd_diff_keys_raw_skips_formatted(patched_get_env):
    result = cmd_diff_keys("a", "pw", "b", "pw", raw=True)
    assert "formatted" not in result


def test_cmd_diff_keys_propagates_error():
    with patch("envault.env_diff_keys.get_env_vars", side_effect=Exception("boom")):
        with pytest.raises(DiffKeysError):
            cmd_diff_keys("missing", "pw", "b", "pw")
