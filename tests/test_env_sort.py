"""Tests for env_sort module."""

import pytest
from unittest.mock import patch, MagicMock

from envault.env_sort import sort_vault, _sort_by_prefix, format_sort_result, SortError


UNSORTED = {"DB_HOST": "localhost", "APP_NAME": "envault", "DB_PORT": "5432", "ZEBRA": "1"}


@pytest.fixture
def mock_sort_deps():
    with patch("envault.env_sort.vault_exists") as exists, \
         patch("envault.env_sort.get_env_vars") as get_env, \
         patch("envault.env_sort.push_env") as push:
        exists.return_value = True
        get_env.return_value = dict(UNSORTED)
        yield exists, get_env, push


def test_sort_raises_if_vault_missing():
    with patch("envault.env_sort.vault_exists", return_value=False):
        with pytest.raises(SortError, match="not found"):
            sort_vault("ghost", "pass")


def test_sort_returns_sorted_keys(mock_sort_deps):
    _, _, _ = mock_sort_deps
    result = sort_vault("myenv", "pass")
    assert result["keys"] == sorted(UNSORTED.keys())


def test_sort_reverse(mock_sort_deps):
    result = sort_vault("myenv", "pass", reverse=True)
    assert result["keys"] == sorted(UNSORTED.keys(), reverse=True)
    assert result["order"] == "desc"


def test_sort_calls_push_when_changed(mock_sort_deps):
    _, _, push = mock_sort_deps
    sort_vault("myenv", "pass")
    push.assert_called_once()


def test_sort_dry_run_skips_push(mock_sort_deps):
    _, _, push = mock_sort_deps
    result = sort_vault("myenv", "pass", dry_run=True)
    push.assert_not_called()
    assert result["dry_run"] is True


def test_sort_no_change_skips_push(mock_sort_deps):
    _, get_env, push = mock_sort_deps
    already_sorted = dict(sorted(UNSORTED.items()))
    get_env.return_value = already_sorted
    result = sort_vault("myenv", "pass")
    push.assert_not_called()
    assert result["changed"] is False


def test_sort_by_prefix_groups_correctly():
    env = {"DB_HOST": "h", "DB_PORT": "p", "APP_NAME": "n", "ZEBRA": "z"}
    result = _sort_by_prefix(env)
    keys = list(result.keys())
    app_idx = keys.index("APP_NAME")
    db_host_idx = keys.index("DB_HOST")
    db_port_idx = keys.index("DB_PORT")
    assert app_idx < db_host_idx < db_port_idx


def test_format_sort_result(mock_sort_deps):
    result = sort_vault("myenv", "pass")
    formatted = format_sort_result(result)
    assert "myenv" in formatted
    assert "asc" in formatted
