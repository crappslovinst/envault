from envault.vault_ops import get_env_vars, push_env
from envault.storage import vault_exists


class DefaultError(Exception):
    pass


def set_defaults(vault: str, password: str, defaults: dict, overwrite: bool = False) -> dict:
    """Apply default key/value pairs to a vault without overwriting existing keys (unless overwrite=True)."""
    if not vault_exists(vault):
        raise DefaultError(f"Vault '{vault}' not found")

    current = get_env_vars(vault, password)
    applied = {}
    skipped = {}

    for key, value in defaults.items():
        if key in current and not overwrite:
            skipped[key] = current[key]
        else:
            applied[key] = value

    if applied:
        updated = {**current, **applied}
        push_env(vault, password, updated)

    return {
        "vault": vault,
        "applied": applied,
        "skipped": skipped,
        "total_applied": len(applied),
        "total_skipped": len(skipped),
    }


def get_defaults_preview(vault: str, password: str, defaults: dict) -> dict:
    """Preview which defaults would be applied without modifying the vault."""
    if not vault_exists(vault):
        raise DefaultError(f"Vault '{vault}' not found")

    current = get_env_vars(vault, password)
    would_apply = {k: v for k, v in defaults.items() if k not in current}
    would_skip = {k: v for k, v in defaults.items() if k in current}

    return {
        "vault": vault,
        "would_apply": would_apply,
        "would_skip": would_skip,
    }


def format_defaults_result(result: dict) -> str:
    lines = [f"Vault: {result['vault']}"]
    if result["applied"]:
        lines.append(f"Applied ({result['total_applied']}):")
        for k, v in result["applied"].items():
            lines.append(f"  + {k}={v}")
    if result["skipped"]:
        lines.append(f"Skipped ({result['total_skipped']}):")
        for k in result["skipped"]:
            lines.append(f"  ~ {k} (already set)")
    if not result["applied"] and not result["skipped"]:
        lines.append("No defaults to apply.")
    return "\n".join(lines)
