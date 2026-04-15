"""Tests for envault/env_permissions.py"""

import pytest
from unittest.mock import patch, MagicMock

from envault.env_permissions import (
    PermissionError,
    set_permission,
    remove_permission,
    get_permission,
    list_permissions,
    check_permission,
)

VAULT = "myvault"
PASS = "secret"


@pytest.fixture
def mock_perm_deps():
    base_data = {}

    def _exists(name):
        return name == VAULT

    def _load(name, pw):
        return dict(base_data)

    def _save(name, data, pw):
        base_data.clear()
        base_data.update(data)

    with patch("envault.env_permissions.vault_exists", side_effect=_exists), \
         patch("envault.env_permissions.load_vault", side_effect=_load), \
         patch("envault.env_permissions.save_vault", side_effect=_save):
        yield base_data


def test_set_permission_returns_summary(mock_perm_deps):
    result = set_permission(VAULT, PASS, "alice", "write")
    assert result["user"] == "alice"
    assert result["role"] == "write"
    assert result["vault"] == VAULT


def test_set_permission_persists(mock_perm_deps):
    set_permission(VAULT, PASS, "bob", "admin")
    assert mock_perm_deps["__permissions__"]["bob"] == "admin"


def test_set_permission_invalid_role(mock_perm_deps):
    with pytest.raises(PermissionError, match="Invalid role"):
        set_permission(VAULT, PASS, "alice", "superuser")


def test_set_permission_raises_if_vault_missing():
    with patch("envault.env_permissions.vault_exists", return_value=False):
        with pytest.raises(PermissionError, match="not found"):
            set_permission("ghost", PASS, "alice", "read")


def test_remove_permission_returns_summary(mock_perm_deps):
    mock_perm_deps["__permissions__"] = {"alice": "read"}
    result = remove_permission(VAULT, PASS, "alice")
    assert result["removed"] is True
    assert result["user"] == "alice"


def test_remove_permission_raises_if_user_missing(mock_perm_deps):
    mock_perm_deps["__permissions__"] = {}
    with pytest.raises(PermissionError, match="no permissions"):
        remove_permission(VAULT, PASS, "nobody")


def test_get_permission_returns_role(mock_perm_deps):
    mock_perm_deps["__permissions__"] = {"carol": "write"}
    role = get_permission(VAULT, PASS, "carol")
    assert role == "write"


def test_get_permission_returns_none_if_unset(mock_perm_deps):
    mock_perm_deps["__permissions__"] = {}
    assert get_permission(VAULT, PASS, "unknown") is None


def test_list_permissions_returns_dict(mock_perm_deps):
    mock_perm_deps["__permissions__"] = {"alice": "read", "bob": "admin"}
    perms = list_permissions(VAULT, PASS)
    assert perms == {"alice": "read", "bob": "admin"}


def test_check_permission_sufficient_role(mock_perm_deps):
    mock_perm_deps["__permissions__"] = {"alice": "write"}
    assert check_permission(VAULT, PASS, "alice", "read") is True
    assert check_permission(VAULT, PASS, "alice", "write") is True


def test_check_permission_insufficient_role(mock_perm_deps):
    mock_perm_deps["__permissions__"] = {"alice": "read"}
    assert check_permission(VAULT, PASS, "alice", "admin") is False


def test_check_permission_user_not_set(mock_perm_deps):
    mock_perm_deps["__permissions__"] = {}
    assert check_permission(VAULT, PASS, "ghost", "read") is False
