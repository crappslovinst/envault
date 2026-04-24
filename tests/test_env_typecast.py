"""Tests for envault.env_typecast."""

import pytest
from unittest.mock import patch

from envault.env_typecast import (
    TypecastError,
    _cast_value,
    typecast_vault,
    format_typecast_result,
)


# --- unit tests for _cast_value ---

def test_cast_int_ok():
    assert _cast_value("42", "int") == 42


def test_cast_int_fails():
    with pytest.raises(TypecastError, match="Cannot cast"):
        _cast_value("abc", "int")


def test_cast_float_ok():
    assert _cast_value("3.14", "float") == pytest.approx(3.14)


def test_cast_float_fails():
    with pytest.raises(TypecastError):
        _cast_value("nope", "float")


def test_cast_bool_truthy_values():
    for v in ("true", "1", "yes", "on", "True", "YES"):
        assert _cast_value(v, "bool") is True


def test_cast_bool_falsy_values():
    for v in ("false", "0", "no", "off", "False", "NO"):
        assert _cast_value(v, "bool") is False


def test_cast_bool_invalid():
    with pytest.raises(TypecastError, match="Cannot cast"):
        _cast_value("maybe", "bool")


def test_cast_str_passthrough():
    assert _cast_value("hello", "str") == "hello"


def test_cast_unknown_type_raises():
    with pytest.raises(TypecastError, match="Unknown target type"):
        _cast_value("x", "list")


# --- typecast_vault tests ---

_FAKE_ENV = {
    "PORT": "8080",
    "DEBUG": "true",
    "RATIO": "0.75",
    "NAME": "myapp",
}


@pytest.fixture
def mock_get_env():
    with patch("envault.env_typecast.get_env_vars", return_value=_FAKE_ENV) as m:
        yield m


def test_typecast_vault_success(mock_get_env):
    schema = {"PORT": "int", "DEBUG": "bool", "RATIO": "float", "NAME": "str"}
    result = typecast_vault("myvault", "pass", schema)
    assert result["success"] == 4
    assert result["failed"] == 0
    assert result["cast"]["PORT"] == 8080
    assert result["cast"]["DEBUG"] is True
    assert result["cast"]["RATIO"] == pytest.approx(0.75)
    assert result["cast"]["NAME"] == "myapp"


def test_typecast_vault_missing_key(mock_get_env):
    result = typecast_vault("myvault", "pass", {"MISSING": "int"})
    assert result["failed"] == 1
    assert "key not found" in result["errors"]["MISSING"]


def test_typecast_vault_cast_error(mock_get_env):
    result = typecast_vault("myvault", "pass", {"NAME": "int"})
    assert result["failed"] == 1
    assert "Cannot cast" in result["errors"]["NAME"]


def test_typecast_vault_raises_on_bad_vault():
    with patch("envault.env_typecast.get_env_vars", side_effect=Exception("not found")):
        with pytest.raises(TypecastError, match="not found"):
            typecast_vault("ghost", "pass", {"X": "int"})


def test_format_typecast_result_contains_sections(mock_get_env):
    result = typecast_vault("myvault", "pass", {"PORT": "int", "NAME": "bool"})
    formatted = format_typecast_result(result)
    assert "Vault" in formatted
    assert "Failed" in formatted
