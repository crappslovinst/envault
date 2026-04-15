"""Tests for envault/env_validate.py"""

import pytest
from unittest.mock import patch
from envault.env_validate import (
    validate_required,
    validate_non_empty,
    validate_pattern,
    ValidationError,
)

SAMPLE_ENV = {
    "DATABASE_URL": "postgres://localhost/mydb",
    "SECRET_KEY": "supersecret",
    "EMPTY_VAR": "",
    "PORT": "8080",
}


@pytest.fixture
def mock_get_env():
    with patch("envault.env_validate.get_env_vars", return_value=SAMPLE_ENV) as m:
        yield m


def test_validate_required_all_present(mock_get_env):
    result = validate_required("myvault", "pass", ["DATABASE_URL", "SECRET_KEY"])
    assert result["valid"] is True
    assert result["missing"] == []
    assert set(result["present"]) == {"DATABASE_URL", "SECRET_KEY"}


def test_validate_required_some_missing(mock_get_env):
    result = validate_required("myvault", "pass", ["DATABASE_URL", "MISSING_KEY"])
    assert result["valid"] is False
    assert "MISSING_KEY" in result["missing"]
    assert "DATABASE_URL" in result["present"]


def test_validate_required_raises_on_bad_vault():
    with patch("envault.env_validate.get_env_vars", side_effect=Exception("bad password")):
        with pytest.raises(ValidationError, match="Could not load vault"):
            validate_required("myvault", "wrongpass", ["KEY"])


def test_validate_non_empty_all_ok(mock_get_env):
    result = validate_non_empty("myvault", "pass", ["DATABASE_URL", "SECRET_KEY"])
    assert result["valid"] is True
    assert result["empty_values"] == []
    assert result["not_found"] == []


def test_validate_non_empty_detects_empty(mock_get_env):
    result = validate_non_empty("myvault", "pass", ["EMPTY_VAR"])
    assert result["valid"] is False
    assert "EMPTY_VAR" in result["empty_values"]


def test_validate_non_empty_detects_not_found(mock_get_env):
    result = validate_non_empty("myvault", "pass", ["NONEXISTENT"])
    assert result["valid"] is False
    assert "NONEXISTENT" in result["not_found"]


def test_validate_non_empty_checks_all_keys_if_none_given(mock_get_env):
    result = validate_non_empty("myvault", "pass", None)
    assert "EMPTY_VAR" in result["empty_values"]
    assert result["valid"] is False


def test_validate_pattern_matches(mock_get_env):
    result = validate_pattern("myvault", "pass", "PORT", r"^\d+$")
    assert result["valid"] is True
    assert result["matched"] is True


def test_validate_pattern_no_match(mock_get_env):
    result = validate_pattern("myvault", "pass", "SECRET_KEY", r"^\d+$")
    assert result["valid"] is False
    assert result["matched"] is False


def test_validate_pattern_raises_if_key_missing(mock_get_env):
    with pytest.raises(ValidationError, match="not found in vault"):
        validate_pattern("myvault", "pass", "GHOST_KEY", r".*")


def test_validate_pattern_raises_on_bad_vault():
    with patch("envault.env_validate.get_env_vars", side_effect=Exception("oops")):
        with pytest.raises(ValidationError, match="Could not load vault"):
            validate_pattern("myvault", "pass", "KEY", r".*")
