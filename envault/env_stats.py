from envault.vault_ops import get_env_vars


class StatsError(Exception):
    pass


def get_stats(vault_name: str, password: str) -> dict:
    """Return statistical summary of a vault's env vars."""
    try:
        env = get_env_vars(vault_name, password)
    except Exception as e:
        raise StatsError(str(e))

    if not env:
        return {
            "total": 0,
            "empty": 0,
            "non_empty": 0,
            "avg_key_length": 0.0,
            "avg_value_length": 0.0,
            "longest_key": None,
            "shortest_key": None,
            "prefixes": {},
        }

    keys = list(env.keys())
    values = list(env.values())
    empty = [v for v in values if v == ""]
    non_empty = [v for v in values if v != ""]

    prefix_counts: dict = {}
    for k in keys:
        if "_" in k:
            prefix = k.split("_")[0]
            prefix_counts[prefix] = prefix_counts.get(prefix, 0) + 1

    return {
        "total": len(keys),
        "empty": len(empty),
        "non_empty": len(non_empty),
        "avg_key_length": round(sum(len(k) for k in keys) / len(keys), 2),
        "avg_value_length": round(
            sum(len(v) for v in non_empty) / len(non_empty), 2
        ) if non_empty else 0.0,
        "longest_key": max(keys, key=len),
        "shortest_key": min(keys, key=len),
        "prefixes": prefix_counts,
    }


def format_stats(stats: dict) -> str:
    lines = [
        f"Total keys    : {stats['total']}",
        f"Non-empty     : {stats['non_empty']}",
        f"Empty         : {stats['empty']}",
        f"Avg key len   : {stats['avg_key_length']}",
        f"Avg value len : {stats['avg_value_length']}",
        f"Longest key   : {stats['longest_key']}",
        f"Shortest key  : {stats['shortest_key']}",
    ]
    if stats["prefixes"]:
        lines.append("Prefixes:")
        for p, c in sorted(stats["prefixes"].items()):
            lines.append(f"  {p}_* : {c}")
    return "\n".join(lines)
