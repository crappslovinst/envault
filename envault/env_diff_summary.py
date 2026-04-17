from envault.vault_ops import get_env_vars
from envault.diff import diff_envs, format_diff


class DiffSummaryError(Exception):
    pass


def summarize_diff(vault_a: str, vault_b: str, password_a: str, password_b: str | None = None) -> dict:
    """Return a structured summary of differences between two vaults."""
    if password_b is None:
        password_b = password_a

    try:
        env_a = get_env_vars(vault_a, password_a)
    except Exception as e:
        raise DiffSummaryError(f"Cannot read vault '{vault_a}': {e}")

    try:
        env_b = get_env_vars(vault_b, password_b)
    except Exception as e:
        raise DiffSummaryError(f"Cannot read vault '{vault_b}': {e}")

    diff = diff_envs(env_a, env_b)

    added = [k for k, s in diff.items() if s == "added"]
    removed = [k for k, s in diff.items() if s == "removed"]
    changed = [k for k, s in diff.items() if s == "changed"]
    unchanged = [k for k, s in diff.items() if s == "unchanged"]

    return {
        "vault_a": vault_a,
        "vault_b": vault_b,
        "added": sorted(added),
        "removed": sorted(removed),
        "changed": sorted(changed),
        "unchanged": sorted(unchanged),
        "total_diff": len(added) + len(removed) + len(changed),
        "formatted": format_diff(diff),
    }


def format_summary(summary: dict) -> str:
    lines = [
        f"Diff: {summary['vault_a']} → {summary['vault_b']}",
        f"  Added:     {len(summary['added'])}",
        f"  Removed:   {len(summary['removed'])}",
        f"  Changed:   {len(summary['changed'])}",
        f"  Unchanged: {len(summary['unchanged'])}",
        f"  Total diff:{summary['total_diff']}",
    ]
    if summary["total_diff"] > 0:
        lines.append("")
        lines.append(summary["formatted"])
    return "\n".join(lines)
