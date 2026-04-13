"""Tests for envault/ttl.py"""

from __future__ import annotations

import time
from unittest.mock import MagicMock, patch

import pytest

from envault.ttl import (
    TTL_KEY,
    EXPIRED_AT_KEY,
    TTLError,
    clear_ttl,
    get_ttl,
    is_expired,
    set_ttl,
)

VAULT = "myvault"
PASSWORD = "secret"


@pytest.fixture()
def mock_storage(tmp_path):
    store = {}

    def _save(name, pw, data):
        store[name] = dict(data)

    def _load(name, pw):
        if name not in store:
            raise KeyError(name)
        return dict(store[name])

    def _exists(name):
        return name in store

    store[VAULT] = {}  # pre-seed vault

    with patch("envault.ttl.save_vault", side_effect=_save), \
         patch("envault.ttl.load_vault", side_effect=_load), \
         patch("envault.ttl.vault_exists", side_effect=_exists):
        yield store


def test_set_ttl_returns_summary(mock_storage):
    result = set_ttl(VAULT, PASSWORD, 300)
    assert result["vault"] == VAULT
    assert result["ttl_seconds"] == 300
    assert result["expires_at"] > time.time()


def test_set_ttl_persists(mock_storage):
    set_ttl(VAULT, PASSWORD, 60)
    assert EXPIRED_AT_KEY in mock_storage[VAULT]
    assert mock_storage[VAULT][TTL_KEY] == 60


def test_set_ttl_raises_if_vault_missing(mock_storage):
    with pytest.raises(TTLError, match="does not exist"):
        set_ttl("ghost", PASSWORD, 60)


def test_set_ttl_raises_on_zero_or_negative(mock_storage):
    with pytest.raises(TTLError, match="positive"):
        set_ttl(VAULT, PASSWORD, 0)
    with pytest.raises(TTLError, match="positive"):
        set_ttl(VAULT, PASSWORD, -10)


def test_get_ttl_returns_none_when_unset(mock_storage):
    result = get_ttl(VAULT, PASSWORD)
    assert result is None


def test_get_ttl_returns_info_after_set(mock_storage):
    set_ttl(VAULT, PASSWORD, 120)
    info = get_ttl(VAULT, PASSWORD)
    assert info is not None
    assert info["ttl_seconds"] == 120
    assert not info["expired"]
    assert info["remaining_seconds"] > 0


def test_get_ttl_shows_expired(mock_storage):
    set_ttl(VAULT, PASSWORD, 1)
    # Manually backdate the expiry
    mock_storage[VAULT][EXPIRED_AT_KEY] = time.time() - 10
    info = get_ttl(VAULT, PASSWORD)
    assert info["expired"] is True
    assert info["remaining_seconds"] == 0


def test_clear_ttl_removes_metadata(mock_storage):
    set_ttl(VAULT, PASSWORD, 60)
    result = clear_ttl(VAULT, PASSWORD)
    assert result["ttl_cleared"] is True
    assert TTL_KEY not in mock_storage[VAULT]
    assert EXPIRED_AT_KEY not in mock_storage[VAULT]


def test_clear_ttl_when_not_set(mock_storage):
    result = clear_ttl(VAULT, PASSWORD)
    assert result["ttl_cleared"] is False


def test_is_expired_false_when_no_ttl(mock_storage):
    assert is_expired(VAULT, PASSWORD) is False


def test_is_expired_true_when_past(mock_storage):
    set_ttl(VAULT, PASSWORD, 1)
    mock_storage[VAULT][EXPIRED_AT_KEY] = time.time() - 5
    assert is_expired(VAULT, PASSWORD) is True


def test_is_expired_false_when_future(mock_storage):
    set_ttl(VAULT, PASSWORD, 9999)
    assert is_expired(VAULT, PASSWORD) is False
