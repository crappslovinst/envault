from envault.vault_ops import push_env, get_env_vars
from envault.storage import vault_exists


class SetError(Exception):
    pass


def set_key(vault: str, password: str, key: str, value: str, overwrite: bool = True) -> dict:
    """Set a single key-value pair in a vault."""
    if not vault_exists(vault):
        raise SetError(f"Vault '{vault}' not found")

    env = get_env_vars(vault, password)

    if key in env and not overwrite:
        return {"vault": vault, "key": key, "status": "skipped", "reason": "key exists"}

    existed = key in env
    env[key] = value
    push_env(vault, password, env)

    return {
        "vault": vault,
        "key": key,
        "value": value,
        "status": "updated" if existed else "created",
    }


def delete_key(vault: str, password: str, key: str) -> dict:
    """Delete a key from a vault."""
    if not vault_exists(vault):
        raise SetError(f"Vault '{vault}' not found")

    env = get_env_vars(vault, password)

    if key not in env:
        raise SetError(f"Key '{key}' not found in vault '{vault}'")

    del env[key]
    push_env(vault, password, env)

    return {"vault": vault, "key": key, "status": "deleted"}


def set_many(vault: str, password: str, pairs: dict, overwrite: bool = True) -> dict:
    """Set multiple key-value pairs at once."""
    if not vault_exists(vault):
        raise SetError(f"Vault '{vault}' not found")

    env = get_env_vars(vault, password)
    results = {}

    for key, value in pairs.items():
        if key in env and not overwrite:
            results[key] = "skipped"
        else:
            existed = key in env
            env[key] = value
            results[key] = "updated" if existed else "created"

    push_env(vault, password, env)
    return {"vault": vault, "results": results, "count": len(results)}
