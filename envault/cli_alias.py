"""CLI commands for vault alias management."""

from __future__ import annotations

from envault.alias import AliasError, list_aliases, remove_alias, resolve_alias, set_alias


def cmd_set_alias(vault_name: str, alias: str, password: str) -> dict:
    """CLI handler: set an alias on a vault."""
    try:
        result = set_alias(vault_name, alias, password)
        return {"ok": True, "message": f"Alias '{alias}' set for vault '{vault_name}'.", **result}
    except AliasError as exc:
        return {"ok": False, "error": str(exc)}


def cmd_remove_alias(vault_name: str, alias: str, password: str) -> dict:
    """CLI handler: remove an alias from a vault."""
    try:
        result = remove_alias(vault_name, alias, password)
        return {"ok": True, "message": f"Alias '{alias}' removed from vault '{vault_name}'.", **result}
    except AliasError as exc:
        return {"ok": False, "error": str(exc)}


def cmd_list_aliases(vault_name: str, password: str) -> dict:
    """CLI handler: list all aliases for a vault."""
    try:
        aliases = list_aliases(vault_name, password)
        return {"ok": True, "vault": vault_name, "aliases": aliases, "count": len(aliases)}
    except AliasError as exc:
        return {"ok": False, "error": str(exc)}


def cmd_resolve_alias(vault_name: str, alias: str, password: str) -> dict:
    """CLI handler: resolve what vault an alias points to."""
    try:
        target = resolve_alias(vault_name, alias, password)
        return {"ok": True, "alias": alias, "resolves_to": target}
    except AliasError as exc:
        return {"ok": False, "error": str(exc)}


def format_alias_list(result: dict) -> str:
    """Human-readable alias list output."""
    if not result.get("ok"):
        return f"Error: {result['error']}"
    aliases = result.get("aliases", [])
    if not aliases:
        return f"No aliases defined for vault '{result['vault']}'."
    lines = [f"Aliases for '{result['vault']}':"]
    for a in aliases:
        lines.append(f"  - {a}")
    return "\n".join(lines)
