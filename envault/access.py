"""Access control for vaults — allow/deny operations per vault."""

from __future__ import annotations

from typing import Literal

from envault.storage import load_vault, save_vault, vault_exists

ACTIONS = ("push", "pull", "export", "delete")

AccessMode = Literal["allow", "deny"]


class AccessError(Exception):
    pass


def _get_acl(vault_data: dict) -> dict:
    return vault_data.setdefault("__acl__", {})


def set_access(vault_name: str, password: str, action: str, mode: AccessMode) -> dict:
    """Set allow/deny for a specific action on a vault."""
    if action not in ACTIONS:
        raise AccessError(f"Unknown action '{action}'. Valid: {ACTIONS}")
    if mode not in ("allow", "deny"):
        raise AccessError(f"Mode must be 'allow' or 'deny', got '{mode}'")
    if not vault_exists(vault_name):
        raise AccessError(f"Vault '{vault_name}' not found")

    data = load_vault(vault_name, password)
    acl = _get_acl(data)
    acl[action] = mode
    save_vault(vault_name, data, password)
    return {"vault": vault_name, "action": action, "mode": mode}


def get_access(vault_name: str, password: str) -> dict:
    """Return the full ACL dict for a vault."""
    if not vault_exists(vault_name):
        raise AccessError(f"Vault '{vault_name}' not found")
    data = load_vault(vault_name, password)
    return dict(_get_acl(data))


def check_access(vault_name: str, password: str, action: str) -> bool:
    """Return True if the action is allowed (default: allow)."""
    if action not in ACTIONS:
        raise AccessError(f"Unknown action '{action}'. Valid: {ACTIONS}")
    if not vault_exists(vault_name):
        raise AccessError(f"Vault '{vault_name}' not found")
    data = load_vault(vault_name, password)
    acl = _get_acl(data)
    return acl.get(action, "allow") == "allow"


def clear_access(vault_name: str, password: str, action: str | None = None) -> dict:
    """Clear ACL entry for one action, or the entire ACL if action is None."""
    if not vault_exists(vault_name):
        raise AccessError(f"Vault '{vault_name}' not found")
    data = load_vault(vault_name, password)
    acl = _get_acl(data)
    if action is None:
        acl.clear()
        cleared = "all"
    else:
        if action not in ACTIONS:
            raise AccessError(f"Unknown action '{action}'. Valid: {ACTIONS}")
        acl.pop(action, None)
        cleared = action
    save_vault(vault_name, data, password)
    return {"vault": vault_name, "cleared": cleared}
