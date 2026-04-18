import pytest
from unittest.mock import patch, MagicMock
from envault.env_upper import upper_keys, format_upper_result, UpperError


@pytest.fixture
def mock_upper_deps():
    with patch("envault.env_upper.vault_exists") as _exists, \
         patch("envault.env_upper.get_env_vars") as _get, \
         patch("envault.env_upper.push_env") as _push:
        yield _exists, _get, _push


def test_upper_keys_raises_if_vault_missing(mock_upper_deps):
    _exists, _get, _push = mock_upper_deps
    _exists.return_value = False
    with pytest.raises(UpperError, match="not found"):
        upper_keys("dev", "pass")


def test_upper_keys_converts_lowercase(mock_upper_deps):
    _exists, _get, _push = mock_upper_deps
    _exists.return_value = True
    _get.return_value = {"db_host": "localhost", "api_key": "abc"}
    result = upper_keys("dev", "pass")
    assert "DB_HOST" in result["env"]
    assert "API_KEY" in result["env"]
    assert result["env"]["DB_HOST"] == "localhost"


def test_upper_keys_already_upper_no_change(mock_upper_deps):
    _exists, _get, _push = mock_upper_deps
    _exists.return_value = True
    _get.return_value = {"DB_HOST": "localhost", "API_KEY": "abc"}
    result = upper_keys("dev", "pass")
    assert result["changed"] == 0
    _push.assert_not_called()


def test_upper_keys_calls_push_when_changed(mock_upper_deps):
    _exists, _get, _push = mock_upper_deps
    _exists.return_value = True
    _get.return_value = {"db_host": "localhost"}
    upper_keys("dev", "pass")
    _push.assert_called_once()


def test_upper_keys_dry_run_skips_push(mock_upper_deps):
    _exists, _get, _push = mock_upper_deps
    _exists.return_value = True
    _get.return_value = {"db_host": "localhost"}
    result = upper_keys("dev", "pass", dry_run=True)
    _push.assert_not_called()
    assert result["dry_run"] is True


def test_upper_keys_returns_correct_counts(mock_upper_deps):
    _exists, _get, _push = mock_upper_deps
    _exists.return_value = True
    _get.return_value = {"db_host": "x", "API_KEY": "y", "port": "5432"}
    result = upper_keys("dev", "pass")
    assert result["total"] == 3
    assert result["changed"] == 2
    assert result["unchanged"] == 1


def test_format_upper_result_contains_vault_name(mock_upper_deps):
    _exists, _get, _push = mock_upper_deps
    _exists.return_value = True
    _get.return_value = {"key": "val"}
    result = upper_keys("staging", "pass")
    formatted = format_upper_result(result)
    assert "staging" in formatted
    assert "Total" in formatted


def test_format_upper_result_dry_run_note(mock_upper_deps):
    _exists, _get, _push = mock_upper_deps
    _exists.return_value = True
    _get.return_value = {"key": "val"}
    result = upper_keys("staging", "pass", dry_run=True)
    formatted = format_upper_result(result)
    assert "dry run" in formatted
