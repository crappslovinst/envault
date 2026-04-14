"""Vault alias management — assign friendly names to vault identifiers."""

from __future__ import annotations

from envault.storage import load_vault, save_vault, vault_exists


class AliasError(Exception):
    pass


def _get_aliases(vault: dict) -> dict[str, str]:
    """Return the alias map stored inside vault metadata."""
    return vault.get("_meta", {}).get("aliases", {})


def set_alias(vault_name: str, alias: str, password: str) -> dict:
    """Add or overwrite *alias* pointing to *vault_name*."""
    if not vault_exists(vault_name):
        raise AliasError(f"Vault '{vault_name}' not found.")
    if not alias or not alias.isidentifier():
        raise AliasError(f"Invalid alias '{alias}': must be a valid identifier.")

    vault = load_vault(vault_name, password)
    meta = vault.setdefault("_meta", {})
    aliases = meta.setdefault("aliases", {})
    aliases[alias] = vault_name
    save_vault(vault_name, vault, password)
    return {"vault": vault_name, "alias": alias, "action": "set"}


def remove_alias(vault_name: str, alias: str, password: str) -> dict:
    """Remove *alias* from *vault_name*."""
    if not vault_exists(vault_name):
        raise AliasError(f"Vault '{vault_name}' not found.")

    vault = load_vault(vault_name, password)
    aliases = _get_aliases(vault)
    if alias not in aliases:
        raise AliasError(f"Alias '{alias}' not found on vault '{vault_name}'.")

    del aliases[alias]
    vault.setdefault("_meta", {})["aliases"] = aliases
    save_vault(vault_name, vault, password)
    return {"vault": vault_name, "alias": alias, "action": "removed"}


def list_aliases(vault_name: str, password: str) -> list[str]:
    """Return all aliases defined for *vault_name*."""
    if not vault_exists(vault_name):
        raise AliasError(f"Vault '{vault_name}' not found.")
    vault = load_vault(vault_name, password)
    return list(_get_aliases(vault).keys())


def resolve_alias(vault_name: str, alias: str, password: str) -> str:
    """Return the vault name that *alias* resolves to."""
    if not vault_exists(vault_name):
        raise AliasError(f"Vault '{vault_name}' not found.")
    vault = load_vault(vault_name, password)
    aliases = _get_aliases(vault)
    if alias not in aliases:
        raise AliasError(f"Alias '{alias}' not found on vault '{vault_name}'.")
    return aliases[alias]
