"""Tests for snapshot create/list/restore/delete functionality."""

from __future__ import annotations

import pytest

from envault.snapshot import (
    SNAPSHOT_KEY,
    SnapshotError,
    create_snapshot,
    delete_snapshot,
    list_snapshots,
    restore_snapshot,
)


VAULT = "test_vault"
PASS = "hunter2"
ENV = {"APP_KEY": "abc", "DB_URL": "postgres://localhost/dev"}


@pytest.fixture(autouse=True)
def patch_vault_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("envault.storage.VAULT_DIR", str(tmp_path))
    monkeypatch.setattr("envault.snapshot.load_vault", _make_load(tmp_path))
    monkeypatch.setattr("envault.snapshot.save_vault", _make_save(tmp_path))
    monkeypatch.setattr("envault.snapshot.vault_exists", _make_exists(tmp_path))


# --- Minimal in-memory vault helpers for tests ---

_store: dict = {}


def _make_load(tmp_path):
    def _load(name, pw):
        return dict(_store.get(name, {}))
    return _load


def _make_save(tmp_path):
    def _save(name, pw, data):
        _store[name] = dict(data)
    return _save


def _make_exists(tmp_path):
    def _exists(name):
        return name in _store
    return _exists


@pytest.fixture(autouse=True)
def reset_store():
    _store.clear()
    _store[VAULT] = dict(ENV)
    yield
    _store.clear()


def test_create_snapshot_returns_summary():
    result = create_snapshot(VAULT, PASS, label="v1")
    assert result["snapshot"] == "v1"
    assert result["vault"] == VAULT
    assert result["count"] == len(ENV)


def test_create_snapshot_persists_in_vault():
    create_snapshot(VAULT, PASS, label="v1")
    snaps = _store[VAULT].get(SNAPSHOT_KEY, {})
    assert "v1" in snaps
    assert snaps["v1"]["vars"] == ENV


def test_create_snapshot_duplicate_label_raises():
    create_snapshot(VAULT, PASS, label="v1")
    with pytest.raises(SnapshotError, match="already exists"):
        create_snapshot(VAULT, PASS, label="v1")


def test_create_snapshot_missing_vault_raises():
    with pytest.raises(SnapshotError, match="not found"):
        create_snapshot("ghost", PASS, label="v1")


def test_list_snapshots_sorted_newest_first():
    create_snapshot(VAULT, PASS, label="snap_a")
    create_snapshot(VAULT, PASS, label="snap_b")
    snaps = list_snapshots(VAULT, PASS)
    assert len(snaps) == 2
    # newest ts should be first (snap_b was created after snap_a)
    assert snaps[0]["label"] == "snap_b"


def test_restore_snapshot_overwrites_env():
    create_snapshot(VAULT, PASS, label="baseline")
    # mutate the vault
    _store[VAULT]["APP_KEY"] = "changed"
    _store[VAULT]["NEW_VAR"] = "extra"
    restore_snapshot(VAULT, PASS, "baseline")
    # after restore, env should match original snapshot vars
    restored_vars = {k: v for k, v in _store[VAULT].items() if k != SNAPSHOT_KEY}
    assert restored_vars == ENV


def test_restore_snapshot_missing_label_raises():
    with pytest.raises(SnapshotError, match="not found"):
        restore_snapshot(VAULT, PASS, "nonexistent")


def test_delete_snapshot_removes_it():
    create_snapshot(VAULT, PASS, label="to_delete")
    delete_snapshot(VAULT, PASS, "to_delete")
    snaps = _store[VAULT].get(SNAPSHOT_KEY, {})
    assert "to_delete" not in snaps


def test_delete_snapshot_missing_raises():
    with pytest.raises(SnapshotError, match="not found"):
        delete_snapshot(VAULT, PASS, "ghost")
