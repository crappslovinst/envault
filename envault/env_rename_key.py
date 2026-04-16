"""Rename a key within a vault, preserving its value."""

from envault.vault_ops import get_env_vars, push_env
from envault.audit import record_event


class RenameKeyError(Exception):
    pass


def rename_key(vault: str, password: str, old_key: str, new_key: str, overwrite: bool = False) -> dict:
    """Rename old_key to new_key inside vault.

    Returns a summary dict with status info.
    """
    try:
        env = get_env_vars(vault, password)
    except Exception as e:
        raise RenameKeyError(f"Could not load vault '{vault}': {e}") from e

    if old_key not in env:
        raise RenameKeyError(f"Key '{old_key}' not found in vault '{vault}'.")

    if new_key in env and not overwrite:
        raise RenameKeyError(
            f"Key '{new_key}' already exists in vault '{vault}'. Use overwrite=True to replace it."
        )

    value = env[old_key]
    updated = {k: v for k, v in env.items() if k != old_key}
    updated[new_key] = value

    push_env(vault, password, updated)
    record_event(vault, "rename_key", {"old_key": old_key, "new_key": new_key})

    return {
        "vault": vault,
        "old_key": old_key,
        "new_key": new_key,
        "value_preserved": True,
        "overwrite": overwrite,
    }
