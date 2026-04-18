from envault.vault_ops import get_env_vars, push_env


class TruncateError(Exception):
    pass


def truncate_values(vault: str, password: str, max_length: int = 64, dry_run: bool = False) -> dict:
    """Truncate all values in a vault to a maximum length."""
    if max_length < 1:
        raise TruncateError("max_length must be at least 1")

    try:
        env = get_env_vars(vault, password)
    except Exception as e:
        raise TruncateError(str(e)) from e

    truncated = {}
    skipped = {}

    for k, v in env.items():
        if len(v) > max_length:
            truncated[k] = v[:max_length]
        else:
            skipped[k] = v

    updated = {**skipped, **truncated}

    if truncated and not dry_run:
        push_env(vault, password, updated)

    return {
        "vault": vault,
        "max_length": max_length,
        "truncated_keys": sorted(truncated.keys()),
        "truncated_count": len(truncated),
        "unchanged_count": len(skipped),
        "dry_run": dry_run,
        "result": updated,
    }


def format_truncate_result(result: dict) -> str:
    lines = [
        f"Vault : {result['vault']}",
        f"Max length : {result['max_length']}",
        f"Truncated  : {result['truncated_count']} key(s)",
        f"Unchanged  : {result['unchanged_count']} key(s)",
    ]
    if result["truncated_keys"]:
        lines.append("Keys truncated:")
        for k in result["truncated_keys"]:
            lines.append(f"  - {k}")
    if result["dry_run"]:
        lines.append("(dry run — no changes saved)")
    return "\n".join(lines)
