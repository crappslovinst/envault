"""Track and report key access/usage statistics for a vault."""

from datetime import datetime, timezone
from envault.storage import load_vault, save_vault, vault_exists


class UsageError(Exception):
    pass


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def _get_usage(vault: dict) -> dict:
    return vault.get("__usage__", {})


def record_access(vault_name: str, key: str, password: str) -> dict:
    """Record that a key was accessed, incrementing its hit count."""
    if not vault_exists(vault_name):
        raise UsageError(f"Vault '{vault_name}' not found.")
    vault = load_vault(vault_name, password)
    usage = _get_usage(vault)
    entry = usage.get(key, {"count": 0, "first_accessed": _ts(), "last_accessed": None})
    entry["count"] += 1
    entry["last_accessed"] = _ts()
    usage[key] = entry
    vault["__usage__"] = usage
    save_vault(vault_name, vault, password)
    return entry


def get_usage(vault_name: str, password: str, key: str = None) -> dict:
    """Return usage stats for all keys or a specific key."""
    if not vault_exists(vault_name):
        raise UsageError(f"Vault '{vault_name}' not found.")
    vault = load_vault(vault_name, password)
    usage = _get_usage(vault)
    if key is not None:
        return {key: usage.get(key, {"count": 0, "first_accessed": None, "last_accessed": None})}
    return usage


def clear_usage(vault_name: str, password: str) -> dict:
    """Clear all usage statistics for a vault."""
    if not vault_exists(vault_name):
        raise UsageError(f"Vault '{vault_name}' not found.")
    vault = load_vault(vault_name, password)
    vault["__usage__"] = {}
    save_vault(vault_name, vault, password)
    return {"status": "cleared", "vault": vault_name}


def top_keys(vault_name: str, password: str, n: int = 5) -> list:
    """Return top N most-accessed keys."""
    usage = get_usage(vault_name, password)
    ranked = sorted(usage.items(), key=lambda x: x[1].get("count", 0), reverse=True)
    return [{"key": k, **v} for k, v in ranked[:n]]
