"""TTL (time-to-live) support for vaults — mark a vault as expiring and check/enforce expiry."""

from __future__ import annotations

import time
from typing import Optional

from envault.storage import load_vault, save_vault, vault_exists


class TTLError(Exception):
    pass


TTL_KEY = "__envault_ttl__"
EXPIRED_AT_KEY = "__envault_expires_at__"


def set_ttl(vault_name: str, password: str, seconds: int) -> dict:
    """Attach a TTL to a vault. Returns updated metadata dict."""
    if not vault_exists(vault_name):
        raise TTLError(f"Vault '{vault_name}' does not exist.")
    if seconds <= 0:
        raise TTLError("TTL must be a positive number of seconds.")

    data = load_vault(vault_name, password)
    expires_at = time.time() + seconds
    data[TTL_KEY] = seconds
    data[EXPIRED_AT_KEY] = expires_at
    save_vault(vault_name, password, data)
    return {"vault": vault_name, "ttl_seconds": seconds, "expires_at": expires_at}


def get_ttl(vault_name: str, password: str) -> Optional[dict]:
    """Return TTL info for a vault, or None if no TTL is set."""
    if not vault_exists(vault_name):
        raise TTLError(f"Vault '{vault_name}' does not exist.")

    data = load_vault(vault_name, password)
    if EXPIRED_AT_KEY not in data:
        return None

    expires_at = data[EXPIRED_AT_KEY]
    remaining = expires_at - time.time()
    return {
        "vault": vault_name,
        "ttl_seconds": data.get(TTL_KEY),
        "expires_at": expires_at,
        "remaining_seconds": max(remaining, 0),
        "expired": remaining <= 0,
    }


def clear_ttl(vault_name: str, password: str) -> dict:
    """Remove TTL metadata from a vault."""
    if not vault_exists(vault_name):
        raise TTLError(f"Vault '{vault_name}' does not exist.")

    data = load_vault(vault_name, password)
    removed = TTL_KEY in data or EXPIRED_AT_KEY in data
    data.pop(TTL_KEY, None)
    data.pop(EXPIRED_AT_KEY, None)
    save_vault(vault_name, password, data)
    return {"vault": vault_name, "ttl_cleared": removed}


def is_expired(vault_name: str, password: str) -> bool:
    """Return True if the vault has a TTL and it has passed."""
    info = get_ttl(vault_name, password)
    if info is None:
        return False
    return info["expired"]
