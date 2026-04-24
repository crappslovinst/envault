import pytest
from unittest.mock import patch
from envault.env_diff_keys import diff_keys, format_diff_keys_result, DiffKeysError


ENV_A = {"APP_HOST": "localhost", "APP_PORT": "8080", "SECRET": "abc"}
ENV_B = {"APP_HOST": "prod.example.com", "DB_URL": "postgres://...", "SECRET": "xyz"}


def _exists(name):
    return name in ("vault_a", "vault_b")


def _get(name, _pw):
    return ENV_A if name == "vault_a" else ENV_B


@pytest.fixture
def patched_get_env():
    with patch("envault.env_diff_keys.vault_exists", side_effect=_exists), \
         patch("envault.env_diff_keys.get_env_vars", side_effect=_get):
        yield


def _side(name, _pw):
    return ENV_A if name == "vault_a" else ENV_B


def test_diff_keys_only_in_a(patched_get_env):
    result = diff_keys("vault_a", "pw", "vault_b", "pw")
    assert "APP_PORT" in result["only_in_a"]


def test_diff_keys_only_in_b(patched_get_env):
    result = diff_keys("vault_a", "pw", "vault_b", "pw")
    assert "DB_URL" in result["only_in_b"]


def test_diff_keys_in_both(patched_get_env):
    result = diff_keys("vault_a", "pw", "vault_b", "pw")
    assert "APP_HOST" in result["in_both"]
    assert "SECRET" in result["in_both"]


def test_diff_keys_counts(patched_get_env):
    result = diff_keys("vault_a", "pw", "vault_b", "pw")
    assert result["shared"] == 2
    assert result["unique_to_a"] == 1
    assert result["unique_to_b"] == 1


def test_diff_keys_totals(patched_get_env):
    result = diff_keys("vault_a", "pw", "vault_b", "pw")
    assert result["total_a"] == 3
    assert result["total_b"] == 3


def test_diff_keys_raises_if_vault_a_missing():
    with patch("envault.env_diff_keys.vault_exists", return_value=False):
        with pytest.raises(DiffKeysError, match="vault_a"):
            diff_keys("vault_a", "pw", "vault_b", "pw")


def test_diff_keys_raises_if_vault_b_missing():
    def _ex(name):
        return name == "vault_a"

    with patch("envault.env_diff_keys.vault_exists", side_effect=_ex):
        with pytest.raises(DiffKeysError, match="vault_b"):
            diff_keys("vault_a", "pw", "vault_b", "pw")


def test_format_diff_keys_result_contains_vault_names(patched_get_env):
    result = diff_keys("vault_a", "pw", "vault_b", "pw")
    formatted = format_diff_keys_result(result)
    assert "vault_a" in formatted
    assert "vault_b" in formatted


def test_format_diff_keys_shows_unique_keys(patched_get_env):
    result = diff_keys("vault_a", "pw", "vault_b", "pw")
    formatted = format_diff_keys_result(result)
    assert "APP_PORT" in formatted
    assert "DB_URL" in formatted


def test_format_diff_keys_shows_counts(patched_get_env):
    result = diff_keys("vault_a", "pw", "vault_b", "pw")
    formatted = format_diff_keys_result(result)
    assert "Shared keys" in formatted
