"""Tests for envault/cli_merge_policy.py"""

import pytest
from unittest.mock import patch

from envault.cli_merge_policy import (
    cmd_set_policy,
    cmd_get_policy,
    cmd_clear_policy,
    format_policy_info,
)
from envault.env_merge_policy import MergePolicyError


@pytest.fixture
def mock_policy_fns():
    with (
        patch("envault.cli_merge_policy.set_policy") as _set,
        patch("envault.cli_merge_policy.get_policy") as _get,
        patch("envault.cli_merge_policy.clear_policy") as _clr,
    ):
        yield _set, _get, _clr


def test_cmd_set_policy_ok(mock_policy_fns):
    _set, _, _ = mock_policy_fns
    _set.return_value = {"vault": "app", "strategy": "ours", "status": "ok"}
    result = cmd_set_policy("app", "pass", "ours")
    assert result["ok"] is True
    assert "ours" in result["message"]


def test_cmd_set_policy_error(mock_policy_fns):
    _set, _, _ = mock_policy_fns
    _set.side_effect = MergePolicyError("Vault 'x' not found.")
    result = cmd_set_policy("x", "pass", "ours")
    assert result["ok"] is False
    assert "not found" in result["error"]


def test_cmd_get_policy_ok(mock_policy_fns):
    _, _get, _ = mock_policy_fns
    _get.return_value = "theirs"
    result = cmd_get_policy("app", "pass")
    assert result["ok"] is True
    assert result["strategy"] == "theirs"
    assert result["is_default"] is False


def test_cmd_get_policy_default(mock_policy_fns):
    _, _get, _ = mock_policy_fns
    _get.return_value = "prompt"
    result = cmd_get_policy("app", "pass")
    assert result["is_default"] is True


def test_cmd_get_policy_error(mock_policy_fns):
    _, _get, _ = mock_policy_fns
    _get.side_effect = MergePolicyError("Vault 'x' not found.")
    result = cmd_get_policy("x", "pass")
    assert result["ok"] is False


def test_cmd_clear_policy_ok(mock_policy_fns):
    _, _, _clr = mock_policy_fns
    _clr.return_value = {"vault": "app", "cleared": True, "status": "ok"}
    result = cmd_clear_policy("app", "pass")
    assert result["ok"] is True
    assert "cleared" in result["message"]


def test_cmd_clear_policy_noop(mock_policy_fns):
    _, _, _clr = mock_policy_fns
    _clr.return_value = {"vault": "app", "cleared": False, "status": "ok"}
    result = cmd_clear_policy("app", "pass")
    assert result["ok"] is True
    assert "No merge policy" in result["message"]


def test_cmd_clear_policy_error(mock_policy_fns):
    _, _, _clr = mock_policy_fns
    _clr.side_effect = MergePolicyError("Vault 'x' not found.")
    result = cmd_clear_policy("x", "pass")
    assert result["ok"] is False


def test_format_policy_info_default():
    out = format_policy_info("app", "prompt", is_default=True)
    assert "app" in out
    assert "prompt" in out
    assert "default" in out


def test_format_policy_info_custom():
    out = format_policy_info("app", "ours", is_default=False)
    assert "ours" in out
    assert "default" not in out
