"""Tests for envault/pin.py"""

import pytest
from unittest.mock import patch, MagicMock

from envault.pin import pin_vault, unpin_vault, get_pin, is_pinned, PinError

VAULT = "myapp"
PASSWORD = "secret"
SNAP_ID = "snap-20240101-abcd"


@pytest.fixture
def mock_pin_deps():
    base_data = {}

    def _exists(name):
        return True

    def _load(name, pw):
        return dict(base_data)

    def _save(name, data, pw):
        base_data.clear()
        base_data.update(data)

    with patch("envault.pin.vault_exists", side_effect=_exists), \
         patch("envault.pin.load_vault", side_effect=_load), \
         patch("envault.pin.save_vault", side_effect=_save):
        yield base_data


def test_pin_vault_returns_summary(mock_pin_deps):
    result = pin_vault(VAULT, PASSWORD, SNAP_ID)
    assert result["vault"] == VAULT
    assert result["pinned_snapshot"] == SNAP_ID
    assert result["status"] == "pinned"


def test_pin_vault_persists(mock_pin_deps):
    pin_vault(VAULT, PASSWORD, SNAP_ID)
    assert mock_pin_deps["__pins__"]["pinned_snapshot"] == SNAP_ID


def test_pin_vault_raises_if_missing():
    with patch("envault.pin.vault_exists", return_value=False):
        with pytest.raises(PinError, match="does not exist"):
            pin_vault(VAULT, PASSWORD, SNAP_ID)


def test_unpin_vault_returns_summary(mock_pin_deps):
    pin_vault(VAULT, PASSWORD, SNAP_ID)
    result = unpin_vault(VAULT, PASSWORD)
    assert result["status"] == "unpinned"
    assert result["vault"] == VAULT


def test_unpin_removes_pin(mock_pin_deps):
    pin_vault(VAULT, PASSWORD, SNAP_ID)
    unpin_vault(VAULT, PASSWORD)
    assert mock_pin_deps.get("__pins__", {}).get("pinned_snapshot") is None


def test_unpin_raises_if_not_pinned(mock_pin_deps):
    with pytest.raises(PinError, match="not pinned"):
        unpin_vault(VAULT, PASSWORD)


def test_get_pin_when_pinned(mock_pin_deps):
    pin_vault(VAULT, PASSWORD, SNAP_ID)
    info = get_pin(VAULT, PASSWORD)
    assert info["pinned"] is True
    assert info["pinned_snapshot"] == SNAP_ID


def test_get_pin_when_not_pinned(mock_pin_deps):
    info = get_pin(VAULT, PASSWORD)
    assert info["pinned"] is False
    assert info["pinned_snapshot"] is None


def test_is_pinned_true(mock_pin_deps):
    pin_vault(VAULT, PASSWORD, SNAP_ID)
    assert is_pinned(VAULT, PASSWORD) is True


def test_is_pinned_false(mock_pin_deps):
    assert is_pinned(VAULT, PASSWORD) is False
