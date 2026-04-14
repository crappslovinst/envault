"""Vault history: track push/pull operations per vault with rollback support."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from envault.storage import load_vault, save_vault, vault_exists
from envault.vault_ops import get_env_vars


class HistoryError(Exception):
    pass


MAX_HISTORY = 20
_HISTORY_KEY = "__history__"


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def record_snapshot(vault_name: str, password: str, action: str) -> dict[str, Any]:
    """Append current env state to the vault's history list."""
    if not vault_exists(vault_name):
        raise HistoryError(f"Vault '{vault_name}' not found.")

    data = load_vault(vault_name, password)
    history: list[dict] = data.get(_HISTORY_KEY, [])

    env_vars = {k: v for k, v in data.items() if not k.startswith("__")}
    entry = {
        "timestamp": _ts(),
        "action": action,
        "snapshot": dict(env_vars),
    }
    history.append(entry)

    # Trim to MAX_HISTORY most recent
    if len(history) > MAX_HISTORY:
        history = history[-MAX_HISTORY:]

    data[_HISTORY_KEY] = history
    save_vault(vault_name, data, password)
    return entry


def get_history(vault_name: str, password: str) -> list[dict[str, Any]]:
    """Return history entries, most recent first."""
    if not vault_exists(vault_name):
        raise HistoryError(f"Vault '{vault_name}' not found.")
    data = load_vault(vault_name, password)
    return list(reversed(data.get(_HISTORY_KEY, [])))


def rollback(vault_name: str, password: str, index: int = 0) -> dict[str, Any]:
    """Restore vault env vars to a historical snapshot (0 = most recent)."""
    entries = get_history(vault_name, password)
    if not entries:
        raise HistoryError(f"No history available for vault '{vault_name}'.")
    if index < 0 or index >= len(entries):
        raise HistoryError(f"History index {index} out of range (0-{len(entries)-1}).")

    target = entries[index]["snapshot"]
    data = load_vault(vault_name, password)

    # Remove existing env keys, preserve meta keys
    meta = {k: v for k, v in data.items() if k.startswith("__")}
    restored = {**meta, **target}
    save_vault(vault_name, restored, password)
    return {"vault": vault_name, "restored_from_index": index, "keys_restored": len(target)}
