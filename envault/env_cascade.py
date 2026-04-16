"""Cascade resolution: merge multiple vaults in priority order."""

from envault.vault_ops import get_env_vars
from envault.storage import vault_exists


class CascadeError(Exception):
    pass


def resolve_cascade(vault_names: list[str], password: str) -> dict:
    """Merge vaults left-to-right, later vaults take priority.

    Args:
        vault_names: ordered list of vault names (lowest to highest priority)
        password: shared password used to decrypt each vault

    Returns:
        Merged dict of env vars with highest-priority values winning.
    """
    if not vault_names:
        raise CascadeError("At least one vault name is required.")

    missing = [v for v in vault_names if not vault_exists(v)]
    if missing:
        raise CascadeError(f"Vault(s) not found: {', '.join(missing)}")

    merged: dict[str, str] = {}
    sources: dict[str, str] = {}  # key -> vault that last set it

    for vault_name in vault_names:
        env_vars = get_env_vars(vault_name, password)
        for key, value in env_vars.items():
            merged[key] = value
            sources[key] = vault_name

    return merged


def resolve_cascade_with_sources(
    vault_names: list[str], password: str
) -> dict[str, dict]:
    """Like resolve_cascade but returns each key's value and winning vault."""
    if not vault_names:
        raise CascadeError("At least one vault name is required.")

    missing = [v for v in vault_names if not vault_exists(v)]
    if missing:
        raise CascadeError(f"Vault(s) not found: {', '.join(missing)}")

    result: dict[str, dict] = {}

    for vault_name in vault_names:
        env_vars = get_env_vars(vault_name, password)
        for key, value in env_vars.items():
            result[key] = {"value": value, "source": vault_name}

    return result
