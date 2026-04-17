import json
import pytest
from unittest.mock import patch, MagicMock
from envault.env_flatten import flatten_vault, format_flatten_result, FlattenError


DB = {"host": "localhost", "port": 5432}
SIMPLE_ENV = {
    "APP_NAME": "myapp",
    "DATABASE": json.dumps(DB),
    "DEBUG": "true",
}


@pytest.fixture
def mock_flatten_deps():
    with patch("envault.env_flatten.get_env_vars") as _get, \
         patch("envault.env_flatten.push_env") as _push:
        yield _get, _push


def test_flatten_expands_json_key(mock_flatten_deps):
    _get, _push = mock_flatten_deps
    _get.return_value = SIMPLE_ENV
    result = flatten_vault("myenv", "pass")
    assert "DATABASE__HOST" in result["env"]
    assert "DATABASE__PORT" in result["env"]
    assert result["env"]["DATABASE__HOST"] == "localhost"


def test_flatten_leaves_plain_values(mock_flatten_deps):
    _get, _push = mock_flatten_deps
    _get.return_value = SIMPLE_ENV
    result = flatten_vault("myenv", "pass")
    assert result["env"]["APP_NAME"] == "myapp"
    assert result["env"]["DEBUG"] == "true"


def test_flatten_counts_are_correct(mock_flatten_deps):
    _get, _push = mock_flatten_deps
    _get.return_value = SIMPLE_ENV
    result = flatten_vault("myenv", "pass")
    assert result["original_count"] == 3
    assert result["flattened_count"] == 4  # DATABASE expands to 2 keys


def test_flatten_calls_push_when_changed(mock_flatten_deps):
    _get, _push = mock_flatten_deps
    _get.return_value = SIMPLE_ENV
    flatten_vault("myenv", "pass")
    _push.assert_called_once()


def test_flatten_dry_run_skips_push(mock_flatten_deps):
    _get, _push = mock_flatten_deps
    _get.return_value = SIMPLE_ENV
    result = flatten_vault("myenv", "pass", dry_run=True)
    _push.assert_not_called()
    assert result["dry_run"] is True


def test_flatten_raises_on_empty_vault(mock_flatten_deps):
    _get, _push = mock_flatten_deps
    _get.return_value = {}
    with pytest.raises(FlattenError):
        flatten_vault("ghost", "pass")


def test_flatten_custom_separator(mock_flatten_deps):
    _get, _push = mock_flatten_deps
    _get.return_value = {"DB": json.dumps({"host": "h"})}
    result = flatten_vault("myenv", "pass", sep=".")
    assert "DB.HOST" in result["env"]


def test_format_flatten_result_contains_info(mock_flatten_deps):
    _get, _push = mock_flatten_deps
    _get.return_value = SIMPLE_ENV
    result = flatten_vault("myenv", "pass")
    formatted = format_flatten_result(result)
    assert "myenv" in formatted
    assert "DATABASE" in formatted
