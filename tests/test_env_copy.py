"""Tests for envault/env_copy.py and envault/cli_env_copy.py."""

import pytest
from unittest.mock import patch, MagicMock

from envault.env_copy import copy_keys, copy_all, CopyError
from envault.cli_env_copy import cmd_copy_keys, cmd_copy_all

SRC = {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "abc"}
DST = {"DB_HOST": "prod-host", "APP_NAME": "myapp"}


@pytest.fixture
def mock_copy_deps():
    with patch("envault.env_copy.get_env_vars") as mock_get, \
         patch("envault.env_copy.push_env") as mock_push, \
         patch("envault.env_copy.record_event") as mock_audit:
        yield mock_get, mock_push, mock_audit


def test_copy_keys_copies_requested(mock_copy_deps):
    mock_get, mock_push, _ = mock_copy_deps
    mock_get.side_effect = [SRC, DST]
    result = copy_keys("src", "p1", "dst", "p2", ["DB_HOST", "SECRET"])
    assert "DB_HOST" in result["copied"]
    assert "SECRET" in result["copied"]
    assert result["missing"] == []
    assert result["skipped"] == []


def test_copy_keys_marks_missing(mock_copy_deps):
    mock_get, mock_push, _ = mock_copy_deps
    mock_get.side_effect = [SRC, DST]
    result = copy_keys("src", "p1", "dst", "p2", ["NONEXISTENT"])
    assert "NONEXISTENT" in result["missing"]
    assert result["copied"] == []


def test_copy_keys_skips_existing_if_no_overwrite(mock_copy_deps):
    mock_get, mock_push, _ = mock_copy_deps
    mock_get.side_effect = [SRC, DST]
    result = copy_keys("src", "p1", "dst", "p2", ["DB_HOST"], overwrite=False)
    assert "DB_HOST" in result["skipped"]
    assert result["copied"] == []


def test_copy_keys_raises_if_src_missing(mock_copy_deps):
    mock_get, _, _ = mock_copy_deps
    mock_get.return_value = None
    with pytest.raises(CopyError, match="Source vault"):
        copy_keys("src", "bad", "dst", "p2", ["KEY"])


def test_copy_keys_records_audit_event(mock_copy_deps):
    mock_get, mock_push, mock_audit = mock_copy_deps
    mock_get.side_effect = [SRC, {}]
    copy_keys("src", "p1", "dst", "p2", ["SECRET"])
    mock_audit.assert_called_once()
    args = mock_audit.call_args[0]
    assert args[0] == "dst"
    assert args[1] == "copy_keys"


def test_copy_all_copies_all_keys(mock_copy_deps):
    mock_get, mock_push, _ = mock_copy_deps
    mock_get.side_effect = [SRC, {}]
    result = copy_all("src", "p1", "dst", "p2")
    assert set(result["copied"]) == set(SRC.keys())


def test_cmd_copy_keys_returns_ok(mock_copy_deps):
    mock_get, mock_push, _ = mock_copy_deps
    mock_get.side_effect = [SRC, DST]
    result = cmd_copy_keys("src", "p1", "dst", "p2", ["SECRET"])
    assert result["ok"] is True
    assert "Copied" in result["message"]


def test_cmd_copy_keys_error_returns_not_ok(mock_copy_deps):
    mock_get, _, _ = mock_copy_deps
    mock_get.return_value = None
    result = cmd_copy_keys("src", "bad", "dst", "p2", ["KEY"])
    assert result["ok"] is False
    assert "error" in result


def test_cmd_copy_all_returns_ok(mock_copy_deps):
    mock_get, mock_push, _ = mock_copy_deps
    mock_get.side_effect = [SRC, {}]
    result = cmd_copy_all("src", "p1", "dst", "p2")
    assert result["ok"] is True
    assert "dst" in result["message"]
