"""Merge policy management for vault environments."""

from envault.storage import load_vault, save_vault, vault_exists

POLICY_KEY = "__merge_policy__"
VALID_STRATEGIES = ("ours", "theirs", "prompt")


class MergePolicyError(Exception):
    pass


def set_policy(vault_name: str, password: str, strategy: str) -> dict:
    """Set the default merge strategy for a vault."""
    if strategy not in VALID_STRATEGIES:
        raise MergePolicyError(
            f"Invalid strategy '{strategy}'. Choose from: {', '.join(VALID_STRATEGIES)}"
        )
    if not vault_exists(vault_name):
        raise MergePolicyError(f"Vault '{vault_name}' not found.")

    data = load_vault(vault_name, password)
    meta = data.get("__meta__", {})
    meta[POLICY_KEY] = strategy
    data["__meta__"] = meta
    save_vault(vault_name, password, data)
    return {"vault": vault_name, "strategy": strategy, "status": "ok"}


def get_policy(vault_name: str, password: str) -> str:
    """Get the default merge strategy for a vault. Returns 'prompt' if unset."""
    if not vault_exists(vault_name):
        raise MergePolicyError(f"Vault '{vault_name}' not found.")

    data = load_vault(vault_name, password)
    return data.get("__meta__", {}).get(POLICY_KEY, "prompt")


def clear_policy(vault_name: str, password: str) -> dict:
    """Remove the merge policy from a vault, reverting to default ('prompt')."""
    if not vault_exists(vault_name):
        raise MergePolicyError(f"Vault '{vault_name}' not found.")

    data = load_vault(vault_name, password)
    meta = data.get("__meta__", {})
    removed = POLICY_KEY in meta
    meta.pop(POLICY_KEY, None)
    data["__meta__"] = meta
    save_vault(vault_name, password, data)
    return {"vault": vault_name, "cleared": removed, "status": "ok"}
