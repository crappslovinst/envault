"""Tests for envault/cli_permissions.py"""

import pytest
from unittest.mock import patch

from envault.cli_permissions import (
    cmd_set_permission,
    cmd_remove_permission,
    cmd_get_permission,
    cmd_list_permissions,
    format_permissions,
)
from envault.env_permissions import PermissionError

VAULT = "myvault"
PASS = "secret"


@pytest.fixture
def mock_perm_fns():
    with patch("envault.cli_permissions.set_permission") as _set, \
         patch("envault.cli_permissions.remove_permission") as _remove, \
         patch("envault.cli_permissions.get_permission") as _get, \
         patch("envault.cli_permissions.list_permissions") as _list:
        yield _set, _remove, _get, _list


def test_cmd_set_permission_ok(mock_perm_fns):
    _set, *_ = mock_perm_fns
    _set.return_value = {"vault": VAULT, "user": "alice", "role": "write"}
    result = cmd_set_permission(VAULT, PASS, "alice", "write")
    assert result["ok"] is True
    assert result["role"] == "write"


def test_cmd_set_permission_error(mock_perm_fns):
    _set, *_ = mock_perm_fns
    _set.side_effect = PermissionError("Invalid role")
    result = cmd_set_permission(VAULT, PASS, "alice", "god")
    assert result["ok"] is False
    assert "Invalid role" in result["error"]


def test_cmd_remove_permission_ok(mock_perm_fns):
    _, _remove, *_ = mock_perm_fns
    _remove.return_value = {"vault": VAULT, "user": "alice", "removed": True}
    result = cmd_remove_permission(VAULT, PASS, "alice")
    assert result["ok"] is True
    assert result["removed"] is True


def test_cmd_remove_permission_error(mock_perm_fns):
    _, _remove, *_ = mock_perm_fns
    _remove.side_effect = PermissionError("no permissions")
    result = cmd_remove_permission(VAULT, PASS, "ghost")
    assert result["ok"] is False


def test_cmd_get_permission_found(mock_perm_fns):
    _, _, _get, _ = mock_perm_fns
    _get.return_value = "admin"
    result = cmd_get_permission(VAULT, PASS, "bob")
    assert result["ok"] is True
    assert result["role"] == "admin"


def test_cmd_get_permission_not_set(mock_perm_fns):
    _, _, _get, _ = mock_perm_fns
    _get.return_value = None
    result = cmd_get_permission(VAULT, PASS, "nobody")
    assert result["ok"] is True
    assert result["role"] is None
    assert "No permission" in result["message"]


def test_cmd_list_permissions_ok(mock_perm_fns):
    *_, _list = mock_perm_fns
    _list.return_value = {"alice": "read", "bob": "admin"}
    result = cmd_list_permissions(VAULT, PASS)
    assert result["ok"] is True
    assert result["permissions"] == {"alice": "read", "bob": "admin"}


def test_format_permissions_non_empty():
    output = format_permissions({"alice": "read", "bob": "admin"})
    assert "alice" in output
    assert "admin" in output


def test_format_permissions_empty():
    output = format_permissions({})
    assert "no permissions" in output
