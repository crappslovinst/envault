"""Reorder keys in a vault according to a specified ordering strategy."""

from envault.vault_ops import get_env_vars, push_env
from envault.storage import vault_exists


class ReorderError(Exception):
    pass


STRATEGIES = ("alpha", "alpha_desc", "by_prefix", "custom")


def reorder_vault(
    vault: str,
    password: str,
    strategy: str = "alpha",
    custom_order: list[str] | None = None,
    dry_run: bool = False,
) -> dict:
    """Reorder keys in a vault.

    Strategies:
      - alpha: alphabetical ascending
      - alpha_desc: alphabetical descending
      - by_prefix: group by prefix (APP_, DB_, etc.), then alpha within group
      - custom: use the order given in custom_order; unknown keys appended at end

    Returns a summary dict.
    """
    if not vault_exists(vault):
        raise ReorderError(f"Vault '{vault}' not found.")
    if strategy not in STRATEGIES:
        raise ReorderError(f"Unknown strategy '{strategy}'. Choose from: {STRATEGIES}")
    if strategy == "custom" and not custom_order:
        raise ReorderError("Strategy 'custom' requires a non-empty custom_order list.")

    env = get_env_vars(vault, password)

    if strategy == "alpha":
        ordered = dict(sorted(env.items()))
    elif strategy == "alpha_desc":
        ordered = dict(sorted(env.items(), reverse=True))
    elif strategy == "by_prefix":
        ordered = _sort_by_prefix(env)
    else:  # custom
        seen = set()
        ordered = {}
        for key in custom_order:
            if key in env:
                ordered[key] = env[key]
                seen.add(key)
        for key in sorted(env.keys()):
            if key not in seen:
                ordered[key] = env[key]

    changed = list(env.keys()) != list(ordered.keys())

    if changed and not dry_run:
        push_env(vault, password, ordered)

    return {
        "vault": vault,
        "strategy": strategy,
        "total": len(ordered),
        "changed": changed,
        "dry_run": dry_run,
        "order": list(ordered.keys()),
    }


def _sort_by_prefix(env: dict) -> dict:
    """Group keys by their prefix (before first underscore), then sort within groups."""
    groups: dict[str, list[str]] = {}
    for key in env:
        prefix = key.split("_")[0] if "_" in key else "__other__"
        groups.setdefault(prefix, []).append(key)

    ordered = {}
    for prefix in sorted(groups):
        for key in sorted(groups[prefix]):
            ordered[key] = env[key]
    return ordered


def format_reorder_result(result: dict) -> str:
    lines = [
        f"Vault  : {result['vault']}",
        f"Strategy: {result['strategy']}",
        f"Total  : {result['total']} keys",
        f"Changed: {result['changed']}",
        f"Dry run: {result['dry_run']}",
    ]
    if result["order"]:
        lines.append("Order  : " + ", ".join(result["order"][:10])
                     + (" ..." if len(result["order"]) > 10 else ""))
    return "\n".join(lines)
