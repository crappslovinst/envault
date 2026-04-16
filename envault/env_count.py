"""Count and summarize keys in a vault."""

from envault.vault_ops import get_env_vars


class CountError(Exception):
    pass


def count_keys(vault_name: str, password: str) -> dict:
    """Return key count statistics for a vault."""
    try:
        env = get_env_vars(vault_name, password)
    except Exception as e:
        raise CountError(str(e)) from e

    total = len(env)
    empty = sum(1 for v in env.values() if not v.strip())
    non_empty = total - empty
    prefixes: dict[str, int] = {}
    for key in env:
        prefix = key.split("_")[0] if "_" in key else key
        prefixes[prefix] = prefixes.get(prefix, 0) + 1

    return {
        "vault": vault_name,
        "total": total,
        "empty": empty,
        "non_empty": non_empty,
        "prefixes": prefixes,
    }


def format_count_result(result: dict) -> str:
    lines = [
        f"Vault : {result['vault']}",
        f"Total : {result['total']}",
        f"Non-empty: {result['non_empty']}",
        f"Empty : {result['empty']}",
    ]
    if result["prefixes"]:
        lines.append("Prefixes:")
        for prefix, count in sorted(result["prefixes"].items()):
            lines.append(f"  {prefix}: {count}")
    return "\n".join(lines)
