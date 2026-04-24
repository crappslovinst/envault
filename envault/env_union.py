"""env_union.py — merge all keys from multiple vaults into one combined set."""

from typing import Optional
from envault.vault_ops import get_env_vars
from envault.storage import vault_exists


class UnionError(Exception):
    pass


def union_vaults(
    vault_names: list[str],
    password: str,
    strategy: str = "first",
) -> dict:
    """Return the union of all keys across the given vaults.

    strategy:
      'first'  — keep the first vault's value when a key appears in multiple vaults
      'last'   — keep the last vault's value
    """
    if len(vault_names) < 2:
        raise UnionError("union requires at least two vault names")

    if strategy not in ("first", "last"):
        raise UnionError(f"unknown strategy '{strategy}'; choose 'first' or 'last'")

    for name in vault_names:
        if not vault_exists(name):
            raise UnionError(f"vault not found: {name}")

    merged: dict[str, str] = {}
    sources: dict[str, str] = {}  # key -> vault that contributed it
    conflicts: dict[str, list[str]] = {}  # key -> list of vaults with that key

    for name in vault_names:
        env = get_env_vars(name, password)
        for k, v in env.items():
            if k in merged:
                conflicts.setdefault(k, [sources[k]])
                conflicts[k].append(name)
                if strategy == "last":
                    merged[k] = v
                    sources[k] = name
            else:
                merged[k] = v
                sources[k] = name

    return {
        "merged": merged,
        "total": len(merged),
        "vaults": vault_names,
        "strategy": strategy,
        "conflicts": conflicts,
        "conflict_count": len(conflicts),
    }


def format_union_result(result: dict) -> str:
    lines = [
        f"Union of {len(result['vaults'])} vaults ({result['strategy']} wins)",
        f"  Total keys : {result['total']}",
        f"  Conflicts  : {result['conflict_count']}",
    ]
    if result["conflicts"]:
        lines.append("  Conflicting keys:")
        for key, vaults in sorted(result["conflicts"].items()):
            lines.append(f"    {key}  (in: {', '.join(vaults)})")
    return "\n".join(lines)
