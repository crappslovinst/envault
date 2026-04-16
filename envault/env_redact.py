"""Redact sensitive values from vault output."""

from envault.vault_ops import get_env_vars
from envault.env_secrets import _is_sensitive

REDACTED = "***REDACTED***"


class RedactError(Exception):
    pass


def redact_env(vault_name: str, password: str, show_keys: list[str] | None = None) -> dict:
    """Return env vars with sensitive values redacted.

    Args:
        vault_name: name of the vault
        password: vault password
        show_keys: optional list of keys to reveal despite being sensitive

    Returns:
        dict with redacted values for sensitive keys
    """
    try:
        env = get_env_vars(vault_name, password)
    except Exception as e:
        raise RedactError(str(e)) from e

    show_keys = set(show_keys or [])
    return {
        k: (v if (not _is_sensitive(k) or k in show_keys) else REDACTED)
        for k, v in env.items()
    }


def format_redact_result(redacted: dict) -> str:
    """Format redacted env vars as a readable string."""
    if not redacted:
        return "(empty)"
    lines = []
    for k, v in sorted(redacted.items()):
        lines.append(f"{k}={v}")
    return "\n".join(lines)


def count_redacted(redacted: dict) -> int:
    """Return how many values were redacted."""
    return sum(1 for v in redacted.values() if v == REDACTED)
