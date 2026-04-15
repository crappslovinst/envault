"""Tests for envault/env_group.py"""

import pytest
from unittest.mock import patch, MagicMock

from envault.env_group import (
    GroupError,
    add_to_group,
    remove_from_group,
    list_groups,
    get_group_members,
    delete_group,
    META_VAULT,
    GROUPS_KEY,
)


@pytest.fixture
def mock_group_deps():
    stored = {}

    def _exists(name):
        return name in stored

    def _load(name, pw):
        return dict(stored.get(name, {}))

    def _save(name, data, pw):
        stored[name] = dict(data)

    with patch("envault.env_group.vault_exists", side_effect=_exists), \
         patch("envault.env_group.load_vault", side_effect=_load), \
         patch("envault.env_group.save_vault", side_effect=_save):
        yield stored


def test_add_to_group_returns_members(mock_group_deps):
    members = add_to_group("prod", "production", "pass")
    assert "prod" in members


def test_add_to_group_no_duplicate(mock_group_deps):
    add_to_group("prod", "production", "pass")
    members = add_to_group("prod", "production", "pass")
    assert members.count("prod") == 1


def test_add_multiple_vaults_to_group(mock_group_deps):
    add_to_group("prod", "production", "pass")
    members = add_to_group("staging", "production", "pass")
    assert "prod" in members
    assert "staging" in members


def test_remove_from_group(mock_group_deps):
    add_to_group("prod", "production", "pass")
    members = remove_from_group("prod", "production", "pass")
    assert "prod" not in members


def test_remove_raises_if_not_member(mock_group_deps):
    add_to_group("prod", "production", "pass")
    with pytest.raises(GroupError, match="not in group"):
        remove_from_group("staging", "production", "pass")


def test_list_groups_empty(mock_group_deps):
    result = list_groups("pass")
    assert result == {}


def test_list_groups_after_add(mock_group_deps):
    add_to_group("prod", "production", "pass")
    groups = list_groups("pass")
    assert "production" in groups


def test_get_group_members(mock_group_deps):
    add_to_group("prod", "production", "pass")
    members = get_group_members("production", "pass")
    assert "prod" in members


def test_get_group_members_raises_if_missing(mock_group_deps):
    with pytest.raises(GroupError, match="does not exist"):
        get_group_members("nonexistent", "pass")


def test_delete_group(mock_group_deps):
    add_to_group("prod", "production", "pass")
    delete_group("production", "pass")
    groups = list_groups("pass")
    assert "production" not in groups


def test_delete_group_raises_if_missing(mock_group_deps):
    with pytest.raises(GroupError, match="does not exist"):
        delete_group("ghost", "pass")
