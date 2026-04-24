"""Summarize a vault: key count, sensitive count, empty count, top prefixes."""

from envault.vault_ops import get_env_vars
from envault.env_secrets import _is_sensitive


class SummarizeError(Exception):
    pass


def summarize_vault(vault_name: str, password: str) -> dict:
    """Return a summary dict for the given vault."""
    try:
        env = get_env_vars(vault_name, password)
    except Exception as exc:
        raise SummarizeError(str(exc)) from exc

    total = len(env)
    empty = sum(1 for v in env.values() if not v.strip())
    sensitive = sum(1 for k in env if _is_sensitive(k))
    non_empty = total - empty

    prefix_counts: dict[str, int] = {}
    for key in env:
        if "_" in key:
            prefix = key.split("_")[0]
            prefix_counts[prefix] = prefix_counts.get(prefix, 0) + 1

    top_prefixes = sorted(prefix_counts.items(), key=lambda x: -x[1])[:5]

    return {
        "vault": vault_name,
        "total": total,
        "empty": empty,
        "non_empty": non_empty,
        "sensitive": sensitive,
        "top_prefixes": dict(top_prefixes),
    }


def format_summary(result: dict) -> str:
    """Return a human-readable summary string."""
    lines = [
        f"Vault     : {result['vault']}",
        f"Total keys: {result['total']}",
        f"Non-empty : {result['non_empty']}",
        f"Empty     : {result['empty']}",
        f"Sensitive : {result['sensitive']}",
    ]
    if result["top_prefixes"]:
        prefix_str = ", ".join(
            f"{p}({c})" for p, c in result["top_prefixes"].items()
        )
        lines.append(f"Top prefix: {prefix_str}")
    return "\n".join(lines)
