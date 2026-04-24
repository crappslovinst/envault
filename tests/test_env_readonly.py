"""Tests for envault.env_readonly and envault.cli_readonly."""

import pytest
from unittest.mock import patch, MagicMock

from envault.env_readonly import (
    ReadonlyError,
    set_readonly,
    get_readonly,
    assert_writable,
    format_readonly_info,
)
from envault.cli_readonly import cmd_set_readonly, cmd_get_readonly

BASE_DATA = {"__env__": {"KEY": "value"}, "__meta__": {}}


@pytest.fixture
def mock_readonly_deps():
    _store = {"data": dict(BASE_DATA)}

    def _exists(name):
        return name == "myvault"

    def _load(name, pw):
        return dict(_store["data"])

    def _save(name, pw, data):
        _store["data"] = data

    with patch("envault.env_readonly.vault_exists", side_effect=_exists), \
         patch("envault.env_readonly.load_vault", side_effect=_load), \
         patch("envault.env_readonly.save_vault", side_effect=_save):
        yield _store


def test_set_readonly_returns_summary(mock_readonly_deps):
    result = set_readonly("myvault", "pw", readonly=True)
    assert result["vault"] == "myvault"
    assert result["readonly"] is True
    assert "enabled" in result["status"]


def test_set_readonly_false_returns_disabled(mock_readonly_deps):
    result = set_readonly("myvault", "pw", readonly=False)
    assert result["readonly"] is False
    assert "disabled" in result["status"]


def test_set_readonly_persists(mock_readonly_deps):
    set_readonly("myvault", "pw", readonly=True)
    info = get_readonly("myvault", "pw")
    assert info["readonly"] is True


def test_get_readonly_default_is_false(mock_readonly_deps):
    info = get_readonly("myvault", "pw")
    assert info["readonly"] is False


def test_set_readonly_raises_if_vault_missing(mock_readonly_deps):
    with pytest.raises(ReadonlyError, match="not found"):
        set_readonly("ghost", "pw")


def test_get_readonly_raises_if_vault_missing(mock_readonly_deps):
    with pytest.raises(ReadonlyError, match="not found"):
        get_readonly("ghost", "pw")


def test_assert_writable_passes_when_not_readonly(mock_readonly_deps):
    assert_writable("myvault", "pw")  # should not raise


def test_assert_writable_raises_when_readonly(mock_readonly_deps):
    set_readonly("myvault", "pw", readonly=True)
    with pytest.raises(ReadonlyError, match="read-only"):
        assert_writable("myvault", "pw")


def test_format_readonly_info_on(mock_readonly_deps):
    info = {"vault": "myvault", "readonly": True}
    out = format_readonly_info(info)
    assert "ON" in out
    assert "myvault" in out


def test_format_readonly_info_off(mock_readonly_deps):
    info = {"vault": "myvault", "readonly": False}
    out = format_readonly_info(info)
    assert "OFF" in out


def test_cmd_set_readonly_ok(mock_readonly_deps):
    result = cmd_set_readonly("myvault", "pw", enable=True)
    assert result["ok"] is True
    assert result["readonly"] is True


def test_cmd_set_readonly_error(mock_readonly_deps):
    result = cmd_set_readonly("ghost", "pw")
    assert result["ok"] is False
    assert "error" in result


def test_cmd_get_readonly_includes_formatted(mock_readonly_deps):
    result = cmd_get_readonly("myvault", "pw")
    assert result["ok"] is True
    assert "formatted" in result


def test_cmd_get_readonly_raw_skips_formatted(mock_readonly_deps):
    result = cmd_get_readonly("myvault", "pw", raw=True)
    assert "formatted" not in result


def test_cmd_get_readonly_error_on_missing_vault(mock_readonly_deps):
    result = cmd_get_readonly("ghost", "pw")
    assert result["ok"] is False
