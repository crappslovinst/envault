"""CLI commands for vault snapshot management."""

from __future__ import annotations

from typing import Optional

from envault.snapshot import (
    SnapshotError,
    create_snapshot,
    delete_snapshot,
    list_snapshots,
    restore_snapshot,
)


def cmd_snapshot_create(vault_name: str, password: str, label: Optional[str] = None) -> dict:
    """CLI handler: create a new snapshot."""
    try:
        result = create_snapshot(vault_name, password, label=label)
        return {"ok": True, "message": f"Snapshot '{result['snapshot']}' created ({result['count']} vars).", **result}
    except SnapshotError as e:
        return {"ok": False, "error": str(e)}


def cmd_snapshot_list(vault_name: str, password: str) -> dict:
    """CLI handler: list all snapshots for a vault."""
    try:
        snaps = list_snapshots(vault_name, password)
        return {"ok": True, "vault": vault_name, "snapshots": snaps, "count": len(snaps)}
    except SnapshotError as e:
        return {"ok": False, "error": str(e)}


def cmd_snapshot_restore(vault_name: str, password: str, label: str) -> dict:
    """CLI handler: restore env vars from a snapshot."""
    try:
        result = restore_snapshot(vault_name, password, label)
        return {"ok": True, "message": f"Restored '{label}' into vault '{vault_name}' ({result['count']} vars).", **result}
    except SnapshotError as e:
        return {"ok": False, "error": str(e)}


def cmd_snapshot_delete(vault_name: str, password: str, label: str) -> dict:
    """CLI handler: delete a snapshot."""
    try:
        result = delete_snapshot(vault_name, password, label)
        return {"ok": True, "message": f"Snapshot '{label}' deleted from vault '{vault_name}'.", **result}
    except SnapshotError as e:
        return {"ok": False, "error": str(e)}


def format_snapshot(snap: dict) -> str:
    """Human-readable single snapshot line."""
    import datetime
    ts = int(snap.get("ts", 0))
    dt = datetime.datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S UTC") if ts else "unknown"
    var_count = len(snap.get("vars", {}))
    return f"  [{snap['label']}]  {dt}  ({var_count} vars)"
