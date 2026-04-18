from envault.vault_ops import get_env_vars, push_env


class DedupeError(Exception):
    pass


def find_duplicate_values(vault: str, password: str) -> dict:
    """Return a dict mapping value -> list of keys that share it."""
    env = get_env_vars(vault, password)
    if env is None:
        raise DedupeError(f"Vault '{vault}' not found")

    value_map: dict = {}
    for key, val in env.items():
        if val not in value_map:
            value_map[val] = []
        value_map[val].append(key)

    return {v: keys for v, keys in value_map.items() if len(keys) > 1}


def dedupe_vault(
    vault: str,
    password: str,
    keep: str = "first",
    dry_run: bool = False,
) -> dict:
    """Remove keys with duplicate values, keeping one per group.

    Args:
        vault: vault name
        password: vault password
        keep: 'first' or 'last' — which key to keep per duplicate group
        dry_run: if True, don't persist changes

    Returns:
        summary dict with removed, kept, total
    """
    env = get_env_vars(vault, password)
    if env is None:
        raise DedupeError(f"Vault '{vault}' not found")

    duplicates = find_duplicate_values(vault, password)
    to_remove: list = []

    for val, keys in duplicates.items():
        ordered = sorted(keys)
        if keep == "last":
            drop = ordered[:-1]
        else:
            drop = ordered[1:]
        to_remove.extend(drop)

    cleaned = {k: v for k, v in env.items() if k not in to_remove}

    if to_remove and not dry_run:
        push_env(vault, password, cleaned)

    return {
        "vault": vault,
        "removed": sorted(to_remove),
        "kept": sorted(cleaned.keys()),
        "total_before": len(env),
        "total_after": len(cleaned),
        "dry_run": dry_run,
    }


def format_dedupe_result(result: dict) -> str:
    lines = [f"Vault: {result['vault']}"]
    lines.append(f"Keys before: {result['total_before']}  after: {result['total_after']}")
    if result["removed"]:
        lines.append("Removed (duplicate values):")
        for k in result["removed"]:
            lines.append(f"  - {k}")
    else:
        lines.append("No duplicate values found.")
    if result["dry_run"]:
        lines.append("(dry run — no changes saved)")
    return "\n".join(lines)
