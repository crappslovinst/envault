"""Tests for import_env and cli_import modules."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from envault.import_env import import_from_dotenv, import_from_json, import_from_shell, ImportError
from envault.cli_import import cmd_import


VAULT = "test-vault"
PASS = "secret"


@pytest.fixture(autouse=True)
def mock_push():
    with patch("envault.import_env.push_env") as m:
        yield m


def test_import_dotenv_basic(tmp_path, mock_push):
    f = tmp_path / ".env"
    f.write_text("FOO=bar\nBAZ=qux\n")
    result = import_from_dotenv(VAULT, PASS, str(f))
    assert result == {"FOO": "bar", "BAZ": "qux"}
    mock_push.assert_called_once_with(VAULT, PASS, result)


def test_import_dotenv_missing_file():
    with pytest.raises(ImportError, match="File not found"):
        import_from_dotenv(VAULT, PASS, "/nonexistent/.env")


def test_import_dotenv_empty_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("# only comments\n\n")
    with pytest.raises(ImportError, match="No valid key-value pairs"):
        import_from_dotenv(VAULT, PASS, str(f))


def test_import_json_basic(tmp_path, mock_push):
    f = tmp_path / "vars.json"
    f.write_text(json.dumps({"KEY": "value", "NUM": 42}))
    result = import_from_json(VAULT, PASS, str(f))
    assert result["KEY"] == "value"
    assert result["NUM"] == "42"


def test_import_json_invalid(tmp_path):
    f = tmp_path / "bad.json"
    f.write_text("not json at all")
    with pytest.raises(ImportError, match="Invalid JSON"):
        import_from_json(VAULT, PASS, str(f))


def test_import_json_non_dict(tmp_path):
    f = tmp_path / "list.json"
    f.write_text(json.dumps(["a", "b"]))
    with pytest.raises(ImportError, match="root must be an object"):
        import_from_json(VAULT, PASS, str(f))


def test_import_shell_basic(tmp_path, mock_push):
    f = tmp_path / "env.sh"
    f.write_text("export FOO=bar\nexport BAZ='hello world'\n")
    result = import_from_shell(VAULT, PASS, str(f))
    assert result["FOO"] == "bar"
    assert result["BAZ"] == "hello world"


def test_import_shell_skips_comments(tmp_path, mock_push):
    f = tmp_path / "env.sh"
    f.write_text("# comment\nexport REAL=yes\n")
    result = import_from_shell(VAULT, PASS, str(f))
    assert "REAL" in result
    assert len(result) == 1


def test_cmd_import_returns_summary(tmp_path, mock_push):
    f = tmp_path / ".env"
    f.write_text("A=1\nB=2\n")
    summary = cmd_import(VAULT, PASS, str(f), fmt="dotenv")
    assert summary["vault"] == VAULT
    assert summary["format"] == "dotenv"
    assert summary["count"] == 2
    assert set(summary["imported_keys"]) == {"A", "B"}


def test_cmd_import_unknown_format(tmp_path):
    with pytest.raises(ValueError, match="Unknown format"):
        cmd_import(VAULT, PASS, "/some/file", fmt="xml")
