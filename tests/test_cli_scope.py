"""Tests for envault/cli_scope.py"""

import pytest
from unittest.mock import patch

from envault.cli_scope import (
    cmd_clear_scope,
    cmd_filter_by_scope,
    cmd_get_scope,
    cmd_set_scope,
)


@pytest.fixture
def mock_scope_fns():
    with (
        patch("envault.cli_scope.set_scope") as _set,
        patch("envault.cli_scope.get_scope") as _get,
        patch("envault.cli_scope.clear_scope") as _clear,
        patch("envault.cli_scope.filter_by_scope") as _filter,
        patch("envault.cli_scope.list_vaults") as _list,
    ):
        yield {"set": _set, "get": _get, "clear": _clear, "filter": _filter, "list": _list}


def test_cmd_set_scope_ok(mock_scope_fns):
    mock_scope_fns["set"].return_value = {"vault": "v", "scope": "dev", "status": "ok"}
    result = cmd_set_scope("v", "pw", "dev")
    assert result["status"] == "ok"
    assert "formatted" in result
    assert "dev" in result["formatted"]


def test_cmd_set_scope_error(mock_scope_fns):
    from envault.env_scope import ScopeError
    mock_scope_fns["set"].side_effect = ScopeError("bad scope")
    result = cmd_set_scope("v", "pw", "bad")
    assert result["status"] == "error"
    assert "bad scope" in result["error"]


def test_cmd_get_scope_ok(mock_scope_fns):
    mock_scope_fns["get"].return_value = "staging"
    result = cmd_get_scope("v", "pw")
    assert result["scope"] == "staging"
    assert result["status"] == "ok"
    assert "formatted" in result


def test_cmd_get_scope_none(mock_scope_fns):
    mock_scope_fns["get"].return_value = None
    result = cmd_get_scope("v", "pw")
    assert result["scope"] is None
    assert "no scope" in result["formatted"]


def test_cmd_clear_scope_cleared(mock_scope_fns):
    mock_scope_fns["clear"].return_value = {"vault": "v", "cleared": True, "status": "ok"}
    result = cmd_clear_scope("v", "pw")
    assert result["cleared"] is True
    assert "cleared" in result["formatted"]


def test_cmd_clear_scope_noop(mock_scope_fns):
    mock_scope_fns["clear"].return_value = {"vault": "v", "cleared": False, "status": "ok"}
    result = cmd_clear_scope("v", "pw")
    assert "no scope" in result["formatted"]


def test_cmd_filter_by_scope_ok(mock_scope_fns):
    mock_scope_fns["list"].return_value = ["v1", "v2"]
    mock_scope_fns["filter"].return_value = ["v1"]
    result = cmd_filter_by_scope("pw", "prod")
    assert result["vaults"] == ["v1"]
    assert result["count"] == 1
    assert result["status"] == "ok"


def test_cmd_filter_by_scope_empty(mock_scope_fns):
    mock_scope_fns["list"].return_value = []
    mock_scope_fns["filter"].return_value = []
    result = cmd_filter_by_scope("pw", "dev")
    assert result["count"] == 0
    assert "No vaults" in result["formatted"]


def test_cmd_filter_by_scope_error(mock_scope_fns):
    from envault.env_scope import ScopeError
    mock_scope_fns["list"].return_value = []
    mock_scope_fns["filter"].side_effect = ScopeError("Invalid scope")
    result = cmd_filter_by_scope("pw", "nope")
    assert result["status"] == "error"
