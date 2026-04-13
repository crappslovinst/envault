"""CLI operations for TTL management."""

from __future__ import annotations

from envault.ttl import TTLError, clear_ttl, get_ttl, is_expired, set_ttl


def cmd_set_ttl(vault_name: str, password: str, seconds: int) -> dict:
    """CLI entry point: set a TTL on a vault."""
    result = set_ttl(vault_name, password, seconds)
    return {
        "status": "ok",
        "message": f"TTL of {seconds}s set on vault '{vault_name}'.",
        **result,
    }


def cmd_get_ttl(vault_name: str, password: str) -> dict:
    """CLI entry point: show TTL info for a vault."""
    info = get_ttl(vault_name, password)
    if info is None:
        return {"status": "ok", "vault": vault_name, "ttl": None, "message": "No TTL set."}
    status = "expired" if info["expired"] else "active"
    return {
        "status": "ok",
        "vault": vault_name,
        "ttl_seconds": info["ttl_seconds"],
        "expires_at": info["expires_at"],
        "remaining_seconds": info["remaining_seconds"],
        "ttl_status": status,
    }


def cmd_clear_ttl(vault_name: str, password: str) -> dict:
    """CLI entry point: remove TTL from a vault."""
    result = clear_ttl(vault_name, password)
    msg = "TTL cleared." if result["ttl_cleared"] else "No TTL was set."
    return {"status": "ok", "message": msg, **result}


def cmd_check_expired(vault_name: str, password: str) -> dict:
    """CLI entry point: check if a vault's TTL has expired."""
    expired = is_expired(vault_name, password)
    return {
        "status": "ok",
        "vault": vault_name,
        "expired": expired,
        "message": "Vault has expired." if expired else "Vault is still valid.",
    }


def format_ttl_info(info: dict) -> str:
    """Human-readable TTL status string."""
    if info.get("ttl") is None:
        return f"{info['vault']}: no TTL"
    remaining = int(info.get("remaining_seconds", 0))
    status = info.get("ttl_status", "unknown")
    return f"{info['vault']}: {status}, {remaining}s remaining"
