"""Scope management for vaults — tag a vault with an environment scope (dev/staging/prod)
and query/filter vaults by scope."""

from envault.storage import load_vault, save_vault, vault_exists

SCOPES = {"dev", "staging", "prod", "test", "local"}


class ScopeError(Exception):
    pass


def _get_meta(vault: dict) -> dict:
    return vault.setdefault("__meta__", {})


def set_scope(vault_name: str, password: str, scope: str) -> dict:
    """Assign a scope to a vault."""
    if not vault_exists(vault_name):
        raise ScopeError(f"Vault '{vault_name}' not found.")
    if scope not in SCOPES:
        raise ScopeError(f"Invalid scope '{scope}'. Choose from: {', '.join(sorted(SCOPES))}")
    vault = load_vault(vault_name, password)
    _get_meta(vault)["scope"] = scope
    save_vault(vault_name, password, vault)
    return {"vault": vault_name, "scope": scope, "status": "ok"}


def get_scope(vault_name: str, password: str) -> str | None:
    """Return the scope of a vault, or None if unset."""
    if not vault_exists(vault_name):
        raise ScopeError(f"Vault '{vault_name}' not found.")
    vault = load_vault(vault_name, password)
    return vault.get("__meta__", {}).get("scope")


def clear_scope(vault_name: str, password: str) -> dict:
    """Remove scope from a vault."""
    if not vault_exists(vault_name):
        raise ScopeError(f"Vault '{vault_name}' not found.")
    vault = load_vault(vault_name, password)
    meta = vault.get("__meta__", {})
    removed = "scope" in meta
    meta.pop("scope", None)
    if "__meta__" in vault:
        vault["__meta__"] = meta
    save_vault(vault_name, password, vault)
    return {"vault": vault_name, "cleared": removed, "status": "ok"}


def filter_by_scope(vault_names: list[str], password: str, scope: str) -> list[str]:
    """Return only the vault names that match the given scope."""
    if scope not in SCOPES:
        raise ScopeError(f"Invalid scope '{scope}'. Choose from: {', '.join(sorted(SCOPES))}")
    result = []
    for name in vault_names:
        try:
            if get_scope(name, password) == scope:
                result.append(name)
        except ScopeError:
            pass
    return result


def format_scope_info(vault_name: str, scope: str | None) -> str:
    if scope:
        return f"{vault_name}: scope={scope}"
    return f"{vault_name}: no scope set"
