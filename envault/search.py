"""Search and filter env vars across vaults."""

from typing import Optional
from envault.vault_ops import get_env_vars
from envault.storage import list_vaults


class SearchError(Exception):
    pass


def search_key(
    key: str,
    password: str,
    vault_name: Optional[str] = None,
    case_sensitive: bool = False,
) -> list[dict]:
    """Search for a key pattern across one or all vaults.

    Returns a list of matches: [{vault, key, value}, ...]
    """
    vaults = [vault_name] if vault_name else list_vaults()
    if not vaults:
        return []

    results = []
    needle = key if case_sensitive else key.lower()

    for vault in vaults:
        try:
            env_vars = get_env_vars(vault, password)
        except Exception:
            # skip vaults we can't decrypt (wrong password, missing, etc.)
            continue

        for k, v in env_vars.items():
            haystack = k if case_sensitive else k.lower()
            if needle in haystack:
                results.append({"vault": vault, "key": k, "value": v})

    return results


def search_value(
    pattern: str,
    password: str,
    vault_name: Optional[str] = None,
    case_sensitive: bool = False,
) -> list[dict]:
    """Search for a value pattern across one or all vaults.

    Returns a list of matches: [{vault, key, value}, ...]
    """
    vaults = [vault_name] if vault_name else list_vaults()
    if not vaults:
        return []

    results = []
    needle = pattern if case_sensitive else pattern.lower()

    for vault in vaults:
        try:
            env_vars = get_env_vars(vault, password)
        except Exception:
            continue

        for k, v in env_vars.items():
            haystack = v if case_sensitive else v.lower()
            if needle in haystack:
                results.append({"vault": vault, "key": k, "value": v})

    return results
