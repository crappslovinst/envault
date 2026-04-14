"""Compare two vaults side-by-side and report differences."""

from typing import Optional
from envault.vault_ops import get_env_vars
from envault.diff import diff_envs, format_diff


class CompareError(Exception):
    pass


def compare_vaults(
    vault_a: str,
    password_a: str,
    vault_b: str,
    password_b: str,
) -> dict:
    """Compare two vaults and return a structured diff result."""
    try:
        env_a = get_env_vars(vault_a, password_a)
    except Exception as e:
        raise CompareError(f"Could not load vault '{vault_a}': {e}") from e

    try:
        env_b = get_env_vars(vault_b, password_b)
    except Exception as e:
        raise CompareError(f"Could not load vault '{vault_b}': {e}") from e

    changes = diff_envs(env_a, env_b)

    return {
        "vault_a": vault_a,
        "vault_b": vault_b,
        "changes": changes,
        "total": len(changes),
        "added": sum(1 for c in changes if c["status"] == "added"),
        "removed": sum(1 for c in changes if c["status"] == "removed"),
        "changed": sum(1 for c in changes if c["status"] == "changed"),
        "unchanged": sum(1 for c in changes if c["status"] == "unchanged"),
    }


def format_compare_result(result: dict, show_unchanged: bool = False) -> str:
    """Render a compare result as a human-readable string."""
    lines = [
        f"Comparing '{result['vault_a']}' \u2192 '{result['vault_b']}'",
        f"  added: {result['added']}  removed: {result['removed']}  "
        f"changed: {result['changed']}  unchanged: {result['unchanged']}",
        "",
    ]
    diff_lines = format_diff(result["changes"], show_unchanged=show_unchanged)
    lines.extend(diff_lines)
    return "\n".join(lines)


def has_differences(result: dict) -> bool:
    """Return True if the compare result contains any meaningful differences.

    Useful for scripting or CI checks where you only care whether the two
    vaults diverge, not the full diff details.
    """
    return result["added"] > 0 or result["removed"] > 0 or result["changed"] > 0
