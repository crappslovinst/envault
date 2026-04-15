"""Reminder/expiry nudges for vault variables — flag keys that haven't been rotated recently."""

from __future__ import annotations

import time
from typing import Any

from envault.vault_ops import get_env_vars
from envault.storage import load_vault, save_vault, vault_exists


class RemindError(Exception):
    pass


def _now() -> float:
    return time.time()


def set_rotation_reminder(vault_name: str, key: str, password: str, interval_days: int) -> dict[str, Any]:
    """Attach a rotation reminder (interval in days) to a specific key in the vault."""
    if not vault_exists(vault_name):
        raise RemindError(f"Vault '{vault_name}' not found.")
    data = load_vault(vault_name, password)
    reminders: dict = data.get("__reminders__", {})
    reminders[key] = {
        "interval_days": interval_days,
        "last_rotated": _now(),
    }
    data["__reminders__"] = reminders
    save_vault(vault_name, password, data)
    return {"vault": vault_name, "key": key, "interval_days": interval_days}


def get_reminders(vault_name: str, password: str) -> dict[str, Any]:
    """Return all reminders stored in the vault."""
    if not vault_exists(vault_name):
        raise RemindError(f"Vault '{vault_name}' not found.")
    data = load_vault(vault_name, password)
    return data.get("__reminders__", {})


def check_due(vault_name: str, password: str) -> list[dict[str, Any]]:
    """Return list of keys whose rotation interval has elapsed."""
    reminders = get_reminders(vault_name, password)
    due = []
    now = _now()
    for key, info in reminders.items():
        elapsed_days = (now - info["last_rotated"]) / 86400
        if elapsed_days >= info["interval_days"]:
            due.append({
                "key": key,
                "interval_days": info["interval_days"],
                "elapsed_days": round(elapsed_days, 2),
            })
    return due


def clear_reminder(vault_name: str, key: str, password: str) -> dict[str, Any]:
    """Remove a rotation reminder for a key."""
    if not vault_exists(vault_name):
        raise RemindError(f"Vault '{vault_name}' not found.")
    data = load_vault(vault_name, password)
    reminders: dict = data.get("__reminders__", {})
    if key not in reminders:
        raise RemindError(f"No reminder set for key '{key}' in vault '{vault_name}'.")
    del reminders[key]
    data["__reminders__"] = reminders
    save_vault(vault_name, password, data)
    return {"vault": vault_name, "key": key, "cleared": True}
