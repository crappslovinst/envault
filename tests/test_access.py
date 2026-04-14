"""Tests for envault/access.py"""

import pytest
from unittest.mock import patch, MagicMock

from envault.access import (
    set_access,
    get_access,
    check_access,
    clear_access,
    AccessError,
)

VAULT = "myvault"
PASSWORD = "secret"


@pytest.fixture
def mock_storage():
    vault_data = {}

    def _exists(name):
        return True

    def _load(name, pw):
        return vault_data.copy()

    def _save(name, data, pw):
        vault_data.clear()
        vault_data.update(data)

    with patch("envault.access.vault_exists", side_effect=_exists), \
         patch("envault.access.load_vault", side_effect=_load), \
         patch("envault.access.save_vault", side_effect=_save):
        yield vault_data


def test_set_access_returns_summary(mock_storage):
    result = set_access(VAULT, PASSWORD, "push", "deny")
    assert result == {"vault": VAULT, "action": "push", "mode": "deny"}


def test_set_access_persists(mock_storage):
    set_access(VAULT, PASSWORD, "pull", "deny")
    acl = get_access(VAULT, PASSWORD)
    assert acl.get("pull") == "deny"


def test_check_access_default_allow(mock_storage):
    assert check_access(VAULT, PASSWORD, "push") is True


def test_check_access_denied_after_set(mock_storage):
    set_access(VAULT, PASSWORD, "export", "deny")
    assert check_access(VAULT, PASSWORD, "export") is False


def test_check_access_allowed_after_set(mock_storage):
    set_access(VAULT, PASSWORD, "delete", "allow")
    assert check_access(VAULT, PASSWORD, "delete") is True


def test_set_access_invalid_action(mock_storage):
    with pytest.raises(AccessError, match="Unknown action"):
        set_access(VAULT, PASSWORD, "nuke", "deny")


def test_set_access_invalid_mode(mock_storage):
    with pytest.raises(AccessError, match="Mode must be"):
        set_access(VAULT, PASSWORD, "push", "maybe")


def test_clear_access_single_action(mock_storage):
    set_access(VAULT, PASSWORD, "pull", "deny")
    clear_access(VAULT, PASSWORD, "pull")
    acl = get_access(VAULT, PASSWORD)
    assert "pull" not in acl


def test_clear_access_all(mock_storage):
    set_access(VAULT, PASSWORD, "push", "deny")
    set_access(VAULT, PASSWORD, "pull", "deny")
    result = clear_access(VAULT, PASSWORD)
    assert result["cleared"] == "all"
    acl = get_access(VAULT, PASSWORD)
    assert acl == {}


def test_raises_if_vault_missing():
    with patch("envault.access.vault_exists", return_value=False):
        with pytest.raises(AccessError, match="not found"):
            get_access(VAULT, PASSWORD)


def test_check_access_invalid_action(mock_storage):
    with pytest.raises(AccessError, match="Unknown action"):
        check_access(VAULT, PASSWORD, "hack")
