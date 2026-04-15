"""Tests for envault/compare.py and envault/cli_compare.py."""

import pytest
from unittest.mock import patch

from envault.compare import compare_vaults, format_compare_result, CompareError
from envault.cli_compare import cmd_compare

ENV_A = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
ENV_B = {"HOST": "prod.example.com", "PORT": "5432", "SENTRY_DSN": "https://x"}


@pytest.fixture()
def mock_get_env():
    """Patch get_env_vars to return canned data."""
    with patch("envault.compare.get_env_vars") as m:
        yield m


@pytest.fixture()
def compare_result(mock_get_env):
    """Return a pre-computed compare result for ENV_A vs ENV_B."""
    mock_get_env.side_effect = [ENV_A, ENV_B]
    return compare_vaults("dev", "pw", "prod", "pw")


def test_compare_returns_summary(mock_get_env):
    mock_get_env.side_effect = [ENV_A, ENV_B]
    result = compare_vaults("dev", "pw", "prod", "pw")
    assert result["vault_a"] == "dev"
    assert result["vault_b"] == "prod"
    assert result["changed"] == 1   # HOST
    assert result["removed"] == 1   # DEBUG
    assert result["added"] == 1     # SENTRY_DSN
    assert result["unchanged"] == 1  # PORT


def test_compare_total_equals_sum(mock_get_env):
    mock_get_env.side_effect = [ENV_A, ENV_B]
    result = compare_vaults("dev", "pw", "prod", "pw")
    assert result["total"] == len(result["changes"])
    assert result["total"] == result["added"] + result["removed"] + result["changed"] + result["unchanged"]


def test_compare_raises_on_bad_vault_a(mock_get_env):
    mock_get_env.side_effect = Exception("not found")
    with pytest.raises(CompareError, match="vault_a" or "dev"):
        compare_vaults("dev", "pw", "prod", "pw")


def test_compare_raises_on_bad_vault_b(mock_get_env):
    mock_get_env.side_effect = [ENV_A, Exception("bad password")]
    with pytest.raises(CompareError, match="prod"):
        compare_vaults("dev", "pw", "prod", "wrongpw")


def test_format_compare_result_contains_vault_names(compare_result):
    text = format_compare_result(compare_result)
    assert "dev" in text
    assert "prod" in text


def test_format_compare_result_hides_unchanged_by_default(compare_result):
    text = format_compare_result(compare_result, show_unchanged=False)
    # PORT is unchanged — should not appear when show_unchanged=False
    assert "PORT" not in text


def test_format_compare_result_shows_unchanged_when_requested(compare_result):
    """PORT is unchanged and should appear when show_unchanged=True."""
    text = format_compare_result(compare_result, show_unchanged=True)
    assert "PORT" in text


def test_cmd_compare_reuses_password_a(mock_get_env):
    mock_get_env.side_effect = [ENV_A, ENV_B]
    result = cmd_compare("dev", "secret", "prod")
    # second call should have used "secret" too
    calls = mock_get_env.call_args_list
    assert calls[1][0][1] == "secret"


def test_cmd_compare_returns_error_dict_on_failure(mock_get_env):
    mock_get_env.side_effect = Exception("vault gone")
    result = cmd_compare("dev", "pw", "prod")
    assert "error" in result


def test_cmd_compare_includes_formatted_key(mock_get_env):
    mock_get_env.side_effect = [ENV_A, ENV_B]
    result = cmd_compare("dev", "pw", "prod", show_unchanged=True)
    assert "formatted" in result
