"""Tests for env_pin_version and cli_pin_version."""

import pytest
from unittest.mock import patch, MagicMock

from envault.env_pin_version import (
    PinVersionError,
    set_version_pin,
    get_version_pin,
    clear_version_pin,
    check_version_compatible,
    format_version_info,
    PIN_VERSION_KEY,
)
from envault.cli_pin_version import (
    cmd_set_version_pin,
    cmd_get_version_pin,
    cmd_clear_version_pin,
    cmd_check_version,
)


@pytest.fixture
def mock_storage():
    store = {}

    def _exists(name):
        return name in store

    def _load(name, pw):
        return dict(store[name])

    def _save(name, pw, data):
        store[name] = dict(data)

    with patch("envault.env_pin_version.vault_exists", side_effect=_exists), \
         patch("envault.env_pin_version.load_vault", side_effect=_load), \
         patch("envault.env_pin_version.save_vault", side_effect=_save):
        store["myapp"] = {"KEY": "val"}
        yield store


def test_set_version_pin_returns_summary(mock_storage):
    result = set_version_pin("myapp", "pw", "1.2.3")
    assert result["vault"] == "myapp"
    assert result["version"] == "1.2.3"
    assert result["status"] == "pinned"


def test_set_version_pin_persists(mock_storage):
    set_version_pin("myapp", "pw", "2.0.0")
    assert mock_storage["myapp"][PIN_VERSION_KEY] == "2.0.0"


def test_set_version_pin_raises_if_vault_missing(mock_storage):
    with pytest.raises(PinVersionError, match="not found"):
        set_version_pin("ghost", "pw", "1.0")


def test_set_version_pin_raises_on_empty_version(mock_storage):
    with pytest.raises(PinVersionError, match="empty"):
        set_version_pin("myapp", "pw", "   ")


def test_get_version_pin_returns_none_when_unset(mock_storage):
    result = get_version_pin("myapp", "pw")
    assert result["pinned"] is False
    assert result["version"] is None


def test_get_version_pin_returns_version_after_set(mock_storage):
    set_version_pin("myapp", "pw", "3.1")
    result = get_version_pin("myapp", "pw")
    assert result["pinned"] is True
    assert result["version"] == "3.1"


def test_clear_version_pin_removes_pin(mock_storage):
    set_version_pin("myapp", "pw", "1.0")
    result = clear_version_pin("myapp", "pw")
    assert result["cleared"] is True
    assert PIN_VERSION_KEY not in mock_storage["myapp"]


def test_clear_version_pin_when_not_set(mock_storage):
    result = clear_version_pin("myapp", "pw")
    assert result["cleared"] is False


def test_check_version_compatible_matches(mock_storage):
    set_version_pin("myapp", "pw", "1.0.0")
    result = check_version_compatible("myapp", "pw", "1.0.0")
    assert result["compatible"] is True


def test_check_version_compatible_mismatch(mock_storage):
    set_version_pin("myapp", "pw", "1.0.0")
    result = check_version_compatible("myapp", "pw", "2.0.0")
    assert result["compatible"] is False


def test_check_version_no_pin_is_incompatible(mock_storage):
    result = check_version_compatible("myapp", "pw", "1.0.0")
    assert result["compatible"] is False


def test_format_version_info_with_pin(mock_storage):
    info = {"vault": "myapp", "version": "4.2"}
    assert "4.2" in format_version_info(info)
    assert "myapp" in format_version_info(info)


def test_format_version_info_no_pin(mock_storage):
    info = {"vault": "myapp", "version": None}
    assert "no version pin" in format_version_info(info)


def test_cmd_get_version_pin_includes_formatted(mock_storage):
    result = cmd_get_version_pin("myapp", "pw", formatted=True)
    assert result["ok"] is True
    assert "formatted" in result


def test_cmd_set_version_pin_ok(mock_storage):
    result = cmd_set_version_pin("myapp", "pw", "5.0")
    assert result["ok"] is True
    assert result["version"] == "5.0"


def test_cmd_clear_version_pin_ok(mock_storage):
    set_version_pin("myapp", "pw", "1.0")
    result = cmd_clear_version_pin("myapp", "pw")
    assert result["ok"] is True
    assert result["cleared"] is True


def test_cmd_check_version_ok(mock_storage):
    set_version_pin("myapp", "pw", "1.0")
    result = cmd_check_version("myapp", "pw", "1.0")
    assert result["ok"] is True
    assert result["compatible"] is True


def test_cmd_set_version_pin_error_on_missing_vault(mock_storage):
    result = cmd_set_version_pin("ghost", "pw", "1.0")
    assert result["ok"] is False
    assert "error" in result
