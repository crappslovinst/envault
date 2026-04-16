"""Mask env var values for safe display (e.g. logs, CLI output)."""

from envault.vault_ops import get_env_vars
from envault.env_secrets import _is_sensitive


class MaskError(Exception):
    pass


def mask_env(vault: str, password: str, show_partial: bool = False, keys: list = None) -> dict:
    """Return env dict with sensitive values masked."""
    try:
        env = get_env_vars(vault, password)
    except Exception as e:
        raise MaskError(str(e)) from e

    masked = {}
    for k, v in env.items():
        if keys and k not in keys:
            masked[k] = v
            continue
        if _is_sensitive(k):
            masked[k] = _mask_value(v, show_partial)
        else:
            masked[k] = v
    return masked


def _mask_value(value: str, show_partial: bool = False) -> str:
    if not value:
        return "****"
    if show_partial and len(value) > 4:
        return value[:2] + "*" * (len(value) - 4) + value[-2:]
    return "*" * min(len(value), 8)


def format_mask_result(masked: dict) -> str:
    lines = []
    for k, v in sorted(masked.items()):
        lines.append(f"{k}={v}")
    return "\n".join(lines)


def count_masked(masked: dict, original: dict) -> int:
    return sum(1 for k in masked if masked[k] != original.get(k))
