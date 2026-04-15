"""Tests for envault/cli_group.py"""

import pytest
from unittest.mock import patch, MagicMock

from envault.cli_group import (
    cmd_group_add,
    cmd_group_remove,
    cmd_group_list,
    cmd_group_members,
    cmd_group_delete,
    format_group_list,
)
from envault.env_group import GroupError


@pytest.fixture
def mock_group_fns():
    with patch("envault.cli_group.add_to_group") as _add, \
         patch("envault.cli_group.remove_from_group") as _remove, \
         patch("envault.cli_group.list_groups") as _list, \
         patch("envault.cli_group.get_group_members") as _members, \
         patch("envault.cli_group.delete_group") as _delete:
        yield {"add": _add, "remove": _remove, "list": _list,
               "members": _members, "delete": _delete}


def test_cmd_group_add_ok(mock_group_fns):
    mock_group_fns["add"].return_value = ["prod"]
    result = cmd_group_add("prod", "production", "pass")
    assert result["ok"] is True
    assert result["vault"] == "prod"
    assert result["group"] == "production"
    assert "prod" in result["members"]


def test_cmd_group_add_error(mock_group_fns):
    mock_group_fns["add"].side_effect = GroupError("oops")
    result = cmd_group_add("prod", "production", "pass")
    assert result["ok"] is False
    assert "oops" in result["error"]


def test_cmd_group_remove_ok(mock_group_fns):
    mock_group_fns["remove"].return_value = []
    result = cmd_group_remove("prod", "production", "pass")
    assert result["ok"] is True


def test_cmd_group_remove_error(mock_group_fns):
    mock_group_fns["remove"].side_effect = GroupError("not in group")
    result = cmd_group_remove("prod", "production", "pass")
    assert result["ok"] is False


def test_cmd_group_list_ok(mock_group_fns):
    mock_group_fns["list"].return_value = {"production": ["prod"]}
    result = cmd_group_list("pass")
    assert result["ok"] is True
    assert result["total"] == 1
    assert "production" in result["groups"]


def test_cmd_group_members_ok(mock_group_fns):
    mock_group_fns["members"].return_value = ["prod", "staging"]
    result = cmd_group_members("production", "pass")
    assert result["ok"] is True
    assert result["count"] == 2


def test_cmd_group_members_error(mock_group_fns):
    mock_group_fns["members"].side_effect = GroupError("does not exist")
    result = cmd_group_members("ghost", "pass")
    assert result["ok"] is False


def test_cmd_group_delete_ok(mock_group_fns):
    result = cmd_group_delete("production", "pass")
    assert result["ok"] is True
    assert result["deleted"] is True


def test_cmd_group_delete_error(mock_group_fns):
    mock_group_fns["delete"].side_effect = GroupError("does not exist")
    result = cmd_group_delete("ghost", "pass")
    assert result["ok"] is False


def test_format_group_list_empty():
    output = format_group_list({})
    assert "No groups" in output


def test_format_group_list_with_members():
    output = format_group_list({"production": ["prod", "staging"]})
    assert "production" in output
    assert "prod" in output
