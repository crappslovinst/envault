"""Snapshot support: save and restore point-in-time copies of a vault's env vars."""

from __future__ import annotations

import time
from typing import Optional

from envault.storage import load_vault, save_vault, vault_exists
from envault.vault_ops import get_env_vars


class SnapshotError(Exception):
    pass


SNAPSHOT_KEY = "__snapshots__"


def _ts() -> str:
    return str(int(time.time()))


def create_snapshot(vault_name: str, password: str, label: Optional[str] = None) -> dict:
    """Save the current env vars as a named snapshot inside the vault."""
    if not vault_exists(vault_name):
        raise SnapshotError(f"Vault '{vault_name}' not found.")

    data = load_vault(vault_name, password)
    snapshots: dict = data.get(SNAPSHOT_KEY, {})

    ts = _ts()
    key = label if label else ts
    if key in snapshots:
        raise SnapshotError(f"Snapshot '{key}' already exists in vault '{vault_name}'.")

    env_vars = {k: v for k, v in data.items() if k != SNAPSHOT_KEY}
    snapshots[key] = {"ts": ts, "label": key, "vars": env_vars}
    data[SNAPSHOT_KEY] = snapshots
    save_vault(vault_name, password, data)

    return {"vault": vault_name, "snapshot": key, "ts": ts, "count": len(env_vars)}


def list_snapshots(vault_name: str, password: str) -> list[dict]:
    """Return all snapshots for a vault, sorted newest first."""
    if not vault_exists(vault_name):
        raise SnapshotError(f"Vault '{vault_name}' not found.")

    data = load_vault(vault_name, password)
    snapshots = data.get(SNAPSHOT_KEY, {})
    return sorted(snapshots.values(), key=lambda s: s["ts"], reverse=True)


def restore_snapshot(vault_name: str, password: str, label: str) -> dict:
    """Overwrite current env vars with those from the named snapshot."""
    if not vault_exists(vault_name):
        raise SnapshotError(f"Vault '{vault_name}' not found.")

    data = load_vault(vault_name, password)
    snapshots = data.get(SNAPSHOT_KEY, {})

    if label not in snapshots:
        raise SnapshotError(f"Snapshot '{label}' not found in vault '{vault_name}'.")

    snap_vars = snapshots[label]["vars"]
    new_data = {k: v for k, v in data.items() if k == SNAPSHOT_KEY}
    new_data.update(snap_vars)
    new_data[SNAPSHOT_KEY] = snapshots
    save_vault(vault_name, password, new_data)

    return {"vault": vault_name, "restored": label, "count": len(snap_vars)}


def delete_snapshot(vault_name: str, password: str, label: str) -> dict:
    """Remove a snapshot from the vault."""
    if not vault_exists(vault_name):
        raise SnapshotError(f"Vault '{vault_name}' not found.")

    data = load_vault(vault_name, password)
    snapshots = data.get(SNAPSHOT_KEY, {})

    if label not in snapshots:
        raise SnapshotError(f"Snapshot '{label}' not found in vault '{vault_name}'.")

    del snapshots[label]
    data[SNAPSHOT_KEY] = snapshots
    save_vault(vault_name, password, data)

    return {"vault": vault_name, "deleted": label}
