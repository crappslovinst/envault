import pytest
from unittest.mock import patch, MagicMock
from envault.env_prefix import add_prefix, remove_prefix, format_prefix_result, PrefixError

BASE_ENV = {"APP_HOST": "localhost", "APP_PORT": "8080", "DEBUG": "true"}


@pytest.fixture
def mock_prefix_deps():
    with patch("envault.env_prefix.get_env_vars") as _get, \
         patch("envault.env_prefix.push_env") as _push:
        _get.return_value = dict(BASE_ENV)
        yield _get, _push


def test_add_prefix_renames_unprefixed_keys(mock_prefix_deps):
    _get, _push = mock_prefix_deps
    result = add_prefix("myvault", "pass", "PRE_")
    renamed_new_keys = [r[1] for r in result["renamed"]]
    assert "PRE_DEBUG" in renamed_new_keys


def test_add_prefix_skips_already_prefixed(mock_prefix_deps):
    _get, _push = mock_prefix_deps
    result = add_prefix("myvault", "pass", "APP_")
    skipped = result["skipped"]
    assert "APP_HOST" in skipped
    assert "APP_PORT" in skipped


def test_add_prefix_calls_push(mock_prefix_deps):
    _get, _push = mock_prefix_deps
    add_prefix("myvault", "pass", "PRE_")
    _push.assert_called_once()


def test_add_prefix_dry_run_skips_push(mock_prefix_deps):
    _get, _push = mock_prefix_deps
    result = add_prefix("myvault", "pass", "PRE_", dry_run=True)
    _push.assert_not_called()
    assert result["dry_run"] is True


def test_remove_prefix_strips_matching_keys(mock_prefix_deps):
    _get, _push = mock_prefix_deps
    result = remove_prefix("myvault", "pass", "APP_")
    renamed_new_keys = [r[1] for r in result["renamed"]]
    assert "HOST" in renamed_new_keys
    assert "PORT" in renamed_new_keys


def test_remove_prefix_skips_non_matching(mock_prefix_deps):
    _get, _push = mock_prefix_deps
    result = remove_prefix("myvault", "pass", "APP_")
    assert "DEBUG" in result["skipped"]


def test_remove_prefix_dry_run_skips_push(mock_prefix_deps):
    _get, _push = mock_prefix_deps
    remove_prefix("myvault", "pass", "APP_", dry_run=True)
    _push.assert_not_called()


def test_add_prefix_raises_on_empty_vault():
    with patch("envault.env_prefix.get_env_vars", return_value={}):
        with pytest.raises(PrefixError):
            add_prefix("empty", "pass", "X_")


def test_format_prefix_result_contains_key_info(mock_prefix_deps):
    _get, _push = mock_prefix_deps
    result = add_prefix("myvault", "pass", "PRE_")
    formatted = format_prefix_result(result)
    assert "PRE_" in formatted
    assert "myvault" in formatted
    assert "Renamed" in formatted
