"""Tests for envault.export and envault.cli_export."""

import json
import os
import pytest

from envault.export import export_env, export_to_file
from envault.cli_export import cmd_export
from unittest.mock import patch


SAMPLE = {"DB_HOST": "localhost", "DB_PASS": 'p@ss"word'}


# ---------------------------------------------------------------------------
# export_env
# ---------------------------------------------------------------------------

def test_export_dotenv_format():
    result = export_env({"KEY": "value"}, fmt="dotenv")
    assert result == 'KEY="value"'


def test_export_shell_format():
    result = export_env({"KEY": "value"}, fmt="shell")
    assert result == 'export KEY="value"'


def test_export_json_format():
    result = export_env({"A": "1", "B": "2"}, fmt="json")
    data = json.loads(result)
    assert data == {"A": "1", "B": "2"}


def test_export_escapes_double_quotes():
    result = export_env({"K": 'say "hi"'}, fmt="dotenv")
    assert result == 'K="say \\"hi\\""'


def test_export_with_prefix_dotenv():
    result = export_env({"HOST": "db"}, fmt="dotenv", prefix="APP_")
    assert "APP_HOST=" in result


def test_export_with_prefix_json():
    result = export_env({"HOST": "db"}, fmt="json", prefix="APP_")
    data = json.loads(result)
    assert "APP_HOST" in data


def test_export_unsupported_format_raises():
    with pytest.raises(ValueError, match="Unsupported format"):
        export_env({"K": "v"}, fmt="xml")


def test_export_multiple_keys_newline_separated():
    result = export_env({"A": "1", "B": "2"}, fmt="dotenv")
    lines = result.splitlines()
    assert len(lines) == 2


def test_export_empty_dict_dotenv():
    """Exporting an empty dict should return an empty string, not crash."""
    result = export_env({}, fmt="dotenv")
    assert result == ""


def test_export_empty_dict_json():
    """Exporting an empty dict as JSON should return a valid empty object."""
    result = export_env({}, fmt="json")
    assert json.loads(result) == {}


# ---------------------------------------------------------------------------
# export_to_file
# ---------------------------------------------------------------------------

def test_export_to_file_creates_file(tmp_path):
    dest = tmp_path / "out.env"
    export_to_file({"X": "y"}, str(dest), fmt="dotenv")
    assert dest.exists()
    assert 'X="y"' in dest.read_text()


def test_export_to_file_ends_with_newline(tmp_path):
    dest = tmp_path / "out.env"
    export_to_file({"X": "y"}, str(dest))
    assert dest.read_text().endswith("\n")


# ---------------------------------------------------------------------------
# cmd_export
# ---------------------------------------------------------------------------

@pytest.fixture()
def mock_vault_vars():
    with patch("envault.cli_export.get_env_vars", return_value={"FOO": "bar"}) as m:
        yield m


def test_cmd_export_returns_string(mock_vault_vars):
    result = cmd_export("myvault", "secret")
    assert isinstance(result, str)
    assert 'FOO="bar"' in result


def test_cmd_export_json(mock_vault_vars):
    result = cmd_export("myvault", "secret", fmt="json")
    data = json.loads(result)
    assert data["FOO"] == "bar"


def test_cmd_export_writes_file(mock_vault_vars, tmp_path):
    dest = tmp_path / "exported.env"
    cmd_export("myvault", "secret", output_path=str(dest))
    assert dest.exists()
    assert 'FOO="bar"' in dest.read_text()
