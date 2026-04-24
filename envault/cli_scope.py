"""CLI commands for vault scope management."""

from envault.env_scope import (
    ScopeError,
    clear_scope,
    filter_by_scope,
    format_scope_info,
    get_scope,
    set_scope,
)
from envault.storage import list_vaults


def cmd_set_scope(vault: str, password: str, scope: str) -> dict:
    """Set the scope of a vault."""
    try:
        result = set_scope(vault, password, scope)
        result["formatted"] = f"Scope for '{vault}' set to '{scope}'."
        return result
    except ScopeError as e:
        return {"error": str(e), "status": "error"}


def cmd_get_scope(vault: str, password: str) -> dict:
    """Get the scope of a vault."""
    try:
        scope = get_scope(vault, password)
        return {
            "vault": vault,
            "scope": scope,
            "formatted": format_scope_info(vault, scope),
            "status": "ok",
        }
    except ScopeError as e:
        return {"error": str(e), "status": "error"}


def cmd_clear_scope(vault: str, password: str) -> dict:
    """Clear the scope of a vault."""
    try:
        result = clear_scope(vault, password)
        msg = f"Scope cleared for '{vault}'." if result["cleared"] else f"'{vault}' had no scope set."
        result["formatted"] = msg
        return result
    except ScopeError as e:
        return {"error": str(e), "status": "error"}


def cmd_filter_by_scope(password: str, scope: str) -> dict:
    """List all vaults matching the given scope."""
    try:
        all_vaults = list_vaults()
        matched = filter_by_scope(all_vaults, password, scope)
        return {
            "scope": scope,
            "vaults": matched,
            "count": len(matched),
            "formatted": "\n".join(matched) if matched else f"No vaults with scope '{scope}'.",
            "status": "ok",
        }
    except ScopeError as e:
        return {"error": str(e), "status": "error"}
