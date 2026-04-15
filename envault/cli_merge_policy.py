"""CLI commands for merge policy management."""

from envault.env_merge_policy import (
    MergePolicyError,
    VALID_STRATEGIES,
    set_policy,
    get_policy,
    clear_policy,
)


def cmd_set_policy(vault_name: str, password: str, strategy: str) -> dict:
    """Set merge strategy for a vault."""
    try:
        result = set_policy(vault_name, password, strategy)
        return {
            "ok": True,
            "message": f"Merge policy for '{vault_name}' set to '{strategy}'.",
            "result": result,
        }
    except MergePolicyError as e:
        return {"ok": False, "error": str(e)}


def cmd_get_policy(vault_name: str, password: str) -> dict:
    """Get the current merge strategy for a vault."""
    try:
        strategy = get_policy(vault_name, password)
        return {
            "ok": True,
            "vault": vault_name,
            "strategy": strategy,
            "is_default": strategy == "prompt",
        }
    except MergePolicyError as e:
        return {"ok": False, "error": str(e)}


def cmd_clear_policy(vault_name: str, password: str) -> dict:
    """Clear the merge policy for a vault."""
    try:
        result = clear_policy(vault_name, password)
        msg = (
            f"Merge policy cleared for '{vault_name}'.'"
            if result["cleared"]
            else f"No merge policy was set for '{vault_name}'."
        )
        return {"ok": True, "message": msg, "result": result}
    except MergePolicyError as e:
        return {"ok": False, "error": str(e)}


def format_policy_info(vault_name: str, strategy: str, is_default: bool) -> str:
    """Format merge policy info for display."""
    label = f"{strategy} (default)" if is_default else strategy
    return f"[{vault_name}] merge policy: {label}"
