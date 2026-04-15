"""Tests for envault/cli_schema.py"""

import json
import pytest
from unittest.mock import patch, MagicMock
from envault.cli_schema import cmd_validate_schema, format_schema_result


VAULT = "myapp"
PASS = "secret"


@pytest.fixture
def schema_file(tmp_path):
    schema = {
        "PORT": {"type": "int", "required": True},
        "DEBUG": {"type": "bool"},
    }
    p = tmp_path / "schema.json"
    p.write_text(json.dumps(schema))
    return str(p)


@pytest.fixture
def mock_validate():
    with patch("envault.cli_schema.validate_schema") as m:
        yield m


def test_cmd_validate_schema_ok(schema_file, mock_validate):
    mock_validate.return_value = {"passed": True, "errors": [], "warnings": []}
    result = cmd_validate_schema(VAULT, PASS, schema_file)
    assert result["status"] == "ok"
    assert result["passed"] is True
    assert result["error_count"] == 0


def test_cmd_validate_schema_failed(schema_file, mock_validate):
    mock_validate.return_value = {
        "passed": False,
        "errors": [{"key": "PORT", "issue": "expected type 'int'"}],
        "warnings": [],
    }
    result = cmd_validate_schema(VAULT, PASS, schema_file)
    assert result["status"] == "failed"
    assert result["error_count"] == 1


def test_cmd_validate_schema_missing_file(mock_validate):
    result = cmd_validate_schema(VAULT, PASS, "/nonexistent/schema.json")
    assert result["status"] == "error"
    assert "not found" in result["message"]


def test_cmd_validate_schema_invalid_json(tmp_path, mock_validate):
    bad = tmp_path / "bad.json"
    bad.write_text("{not valid json")
    result = cmd_validate_schema(VAULT, PASS, str(bad))
    assert result["status"] == "error"
    assert "Invalid JSON" in result["message"]


def test_format_schema_result_ok():
    result = {
        "status": "ok",
        "vault": "myapp",
        "passed": True,
        "errors": [],
        "warnings": [],
        "error_count": 0,
        "warning_count": 0,
    }
    out = format_schema_result(result)
    assert "passed" in out
    assert "myapp" in out


def test_format_schema_result_failed():
    result = {
        "status": "failed",
        "vault": "myapp",
        "passed": False,
        "errors": [{"key": "PORT", "issue": "expected type 'int'"}],
        "warnings": [{"key": "EXTRA", "issue": "key not present in vault"}],
        "error_count": 1,
        "warning_count": 1,
    }
    out = format_schema_result(result)
    assert "failed" in out
    assert "PORT" in out
    assert "EXTRA" in out
    assert "1 error" in out


def test_format_schema_result_error():
    result = {"status": "error", "message": "vault not found"}
    out = format_schema_result(result)
    assert "[error]" in out
    assert "vault not found" in out
