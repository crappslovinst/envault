"""Pad env values to a minimum length with a fill character."""

from envault.vault_ops import get_env_vars, push_env
from envault.storage import vault_exists


class PadError(Exception):
    pass


def pad_values(
    vault_name: str,
    password: str,
    min_length: int,
    fill_char: str = "0",
    keys: list[str] | None = None,
    dry_run: bool = False,
) -> dict:
    if not vault_exists(vault_name):
        raise PadError(f"Vault '{vault_name}' not found.")
    if len(fill_char) != 1:
        raise PadError("fill_char must be exactly one character.")
    if min_length < 1:
        raise PadError("min_length must be at least 1.")

    env = get_env_vars(vault_name, password)
    padded = {}
    skipped = []

    for k, v in env.items():
        if keys and k not in keys:
            continue
        if len(v) < min_length:
            padded[k] = v.ljust(min_length, fill_char)
        else:
            skipped.append(k)

    if padded and not dry_run:
        updated = {**env, **padded}
        push_env(vault_name, password, updated)

    return {
        "vault": vault_name,
        "padded": padded,
        "skipped": skipped,
        "total_padded": len(padded),
        "dry_run": dry_run,
    }


def format_pad_result(result: dict) -> str:
    lines = [f"Vault: {result['vault']}"]
    if result["dry_run"]:
        lines.append("(dry run — no changes written)")
    if result["padded"]:
        lines.append(f"Padded {result['total_padded']} key(s):")
        for k, v in result["padded"].items():
            lines.append(f"  {k} => {v!r}")
    else:
        lines.append("No values needed padding.")
    return "\n".join(lines)
