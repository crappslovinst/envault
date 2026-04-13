"""Vault sharing: export/import encrypted vault bundles for sharing between users."""

import json
import base64
from typing import Optional

from envault.vault_ops import get_env_vars, push_env
from envault.crypto import encrypt, decrypt
from envault.audit import record_event


class ShareError(Exception):
    pass


def export_bundle(vault_name: str, password: str, bundle_password: str) -> str:
    """Export a vault as an encrypted base64 bundle string."""
    env_vars = get_env_vars(vault_name, password)
    if env_vars is None:
        raise ShareError(f"Vault '{vault_name}' not found or wrong password.")

    payload = json.dumps({"vault": vault_name, "env": env_vars})
    encrypted = encrypt(payload, bundle_password)
    bundle = base64.urlsafe_b64encode(encrypted.encode()).decode()

    record_event(vault_name, "share_export", {"bundle_password_hint": "<redacted>"})
    return bundle


def import_bundle(
    bundle: str,
    bundle_password: str,
    new_password: str,
    vault_name: Optional[str] = None,
) -> dict:
    """Import a vault from an encrypted bundle string."""
    try:
        raw = base64.urlsafe_b64decode(bundle.encode()).decode()
    except Exception as exc:
        raise ShareError(f"Invalid bundle format: {exc}") from exc

    try:
        payload = decrypt(raw, bundle_password)
    except Exception as exc:
        raise ShareError(f"Failed to decrypt bundle — wrong password? ({exc})") from exc

    try:
        data = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise ShareError(f"Bundle payload is corrupted: {exc}") from exc

    target_vault = vault_name or data.get("vault", "imported")
    env_vars = data.get("env", {})

    if not isinstance(env_vars, dict):
        raise ShareError("Bundle env data is not a valid mapping.")

    push_env(target_vault, new_password, env_vars)
    record_event(target_vault, "share_import", {"source_vault": data.get("vault")})

    return {"vault": target_vault, "keys_imported": len(env_vars)}


def save_bundle_to_file(bundle: str, path: str) -> None:
    """Write a bundle string to a file."""
    with open(path, "w") as fh:
        fh.write(bundle)


def load_bundle_from_file(path: str) -> str:
    """Read a bundle string from a file."""
    try:
        with open(path, "r") as fh:
            return fh.read().strip()
    except FileNotFoundError as exc:
        raise ShareError(f"Bundle file not found: {path}") from exc
