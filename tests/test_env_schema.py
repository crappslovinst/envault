"""Tests for envault/env_schema.py"""

import pytest
from unittest.mock import patch
from envault.env_schema import validate_schema, SchemaError


VAULT = "myapp"
PASS = "secret"

ENV = {
    "PORT": "8080",
    "DEBUG": "true",
    "RATIO": "3.14",
    "APP_NAME": "envault",
    "MODE": "production",
}


@pytest.fixture(autouse=True)
def mock_get_env(monkeypatch):
    monkeypatch.setattr("envault.env_schema.get_env_vars", lambda v, p: dict(ENV))


def test_validate_passes_clean_schema():
    schema = {"PORT": {"type": "int"}, "APP_NAME": {"type": "str"}}
    result = validate_schema(VAULT, PASS, schema)
    assert result["passed"] is True
    assert result["errors"] == []


def test_validate_detects_wrong_type():
    schema = {"APP_NAME": {"type": "int"}}
    result = validate_schema(VAULT, PASS, schema)
    assert not result["passed"]
    assert any(e["key"] == "APP_NAME" for e in result["errors"])


def test_validate_bool_type_passes():
    schema = {"DEBUG": {"type": "bool"}}
    result = validate_schema(VAULT, PASS, schema)
    assert result["passed"] is True


def test_validate_float_type_passes():
    schema = {"RATIO": {"type": "float"}}
    result = validate_schema(VAULT, PASS, schema)
    assert result["passed"] is True


def test_validate_pattern_match():
    schema = {"PORT": {"pattern": r"\d+"}}
    result = validate_schema(VAULT, PASS, schema)
    assert result["passed"] is True


def test_validate_pattern_mismatch():
    schema = {"APP_NAME": {"pattern": r"\d+"}}
    result = validate_schema(VAULT, PASS, schema)
    assert not result["passed"]
    assert any("pattern" in e["issue"] for e in result["errors"])


def test_validate_allowed_values_pass():
    schema = {"MODE": {"allowed": ["production", "staging", "development"]}}
    result = validate_schema(VAULT, PASS, schema)
    assert result["passed"] is True


def test_validate_allowed_values_fail():
    schema = {"MODE": {"allowed": ["staging", "development"]}}
    result = validate_schema(VAULT, PASS, schema)
    assert not result["passed"]
    assert any("allowed" in e["issue"] for e in result["errors"])


def test_validate_required_missing_key():
    schema = {"MISSING_KEY": {"required": True}}
    result = validate_schema(VAULT, PASS, schema)
    assert not result["passed"]
    assert any(e["key"] == "MISSING_KEY" for e in result["errors"])


def test_validate_optional_missing_key_is_warning():
    schema = {"MISSING_KEY": {"required": False}}
    result = validate_schema(VAULT, PASS, schema)
    assert result["passed"] is True
    assert any(w["key"] == "MISSING_KEY" for w in result["warnings"])


def test_validate_raises_on_unsupported_type():
    schema = {"PORT": {"type": "uuid"}}
    with pytest.raises(SchemaError, match="Unsupported type"):
        validate_schema(VAULT, PASS, schema)


def test_validate_raises_if_vault_missing(monkeypatch):
    monkeypatch.setattr("envault.env_schema.get_env_vars", lambda v, p: (_ for _ in ()).throw(Exception("not found")))
    with pytest.raises(SchemaError):
        validate_schema("ghost", PASS, {"KEY": {}})
