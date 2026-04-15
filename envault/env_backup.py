"""Backup and restore vaults to/from plain JSON files (unencrypted export for safekeeping)."""

import json
import os
from datetime import datetime, timezone

from envault.vault_ops import get_env_vars, push_env
from envault.storage import vault_exists
from envault.audit import record_event


class BackupError(Exception):
    pass


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def backup_vault(vault_name: str, password: str, dest_path: str) -> dict:
    """Export a vault's env vars to an unencrypted JSON backup file."""
    if not vault_exists(vault_name):
        raise BackupError(f"Vault '{vault_name}' does not exist.")

    env_vars = get_env_vars(vault_name, password)

    payload = {
        "vault": vault_name,
        "backed_up_at": _ts(),
        "vars": env_vars,
    }

    with open(dest_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    record_event(vault_name, "backup", {"dest": dest_path})

    return {
        "vault": vault_name,
        "dest": dest_path,
        "keys_backed_up": len(env_vars),
        "backed_up_at": payload["backed_up_at"],
    }


def restore_vault(src_path: str, vault_name: str, password: str, overwrite: bool = False) -> dict:
    """Restore a vault from a JSON backup file."""
    if not os.path.isfile(src_path):
        raise BackupError(f"Backup file not found: '{src_path}'")

    with open(src_path, "r", encoding="utf-8") as f:
        try:
            payload = json.load(f)
        except json.JSONDecodeError as exc:
            raise BackupError(f"Invalid backup file: {exc}") from exc

    if "vars" not in payload or not isinstance(payload["vars"], dict):
        raise BackupError("Backup file is missing 'vars' mapping.")

    if vault_exists(vault_name) and not overwrite:
        raise BackupError(
            f"Vault '{vault_name}' already exists. Pass overwrite=True to replace it."
        )

    push_env(vault_name, password, payload["vars"])
    record_event(vault_name, "restore", {"src": src_path})

    return {
        "vault": vault_name,
        "src": src_path,
        "keys_restored": len(payload["vars"]),
        "original_vault": payload.get("vault"),
        "original_backed_up_at": payload.get("backed_up_at"),
    }
