"""Clamp (truncate or pad) all values in a vault to a fixed length range."""

from envault.vault_ops import get_env_vars, push_env
from envault.storage import vault_exists


class ClampError(Exception):
    pass


def clamp_values(
    vault: str,
    password: str,
    min_len: int = 0,
    max_len: int = 255,
    pad_char: str = " ",
    dry_run: bool = False,
) -> dict:
    """Clamp all values in a vault so that min_len <= len(value) <= max_len.

    Short values are right-padded with *pad_char*; long values are truncated.
    Returns a summary dict describing what changed.
    """
    if not vault_exists(vault):
        raise ClampError(f"Vault '{vault}' not found.")
    if min_len < 0 or max_len < 0:
        raise ClampError("min_len and max_len must be non-negative.")
    if min_len > max_len:
        raise ClampError("min_len must be <= max_len.")
    if len(pad_char) != 1:
        raise ClampError("pad_char must be exactly one character.")

    env = get_env_vars(vault, password)
    updated: dict[str, str] = {}
    padded: list[str] = []
    truncated: list[str] = []

    for key, value in env.items():
        length = len(value)
        if length < min_len:
            new_val = value.ljust(min_len, pad_char)
            updated[key] = new_val
            padded.append(key)
        elif length > max_len:
            new_val = value[:max_len]
            updated[key] = new_val
            truncated.append(key)
        else:
            updated[key] = value

    changed = bool(padded or truncated)
    if changed and not dry_run:
        push_env(vault, password, updated)

    return {
        "vault": vault,
        "min_len": min_len,
        "max_len": max_len,
        "total": len(env),
        "padded": sorted(padded),
        "truncated": sorted(truncated),
        "changed": changed,
        "dry_run": dry_run,
    }


def format_clamp_result(result: dict) -> str:
    lines = [
        f"Vault : {result['vault']}",
        f"Range : [{result['min_len']}, {result['max_len']}]",
        f"Total : {result['total']}",
        f"Padded    ({len(result['padded'])}): {', '.join(result['padded']) or 'none'}",
        f"Truncated ({len(result['truncated'])}): {', '.join(result['truncated']) or 'none'}",
    ]
    if result["dry_run"]:
        lines.append("(dry run — no changes written)")
    return "\n".join(lines)
