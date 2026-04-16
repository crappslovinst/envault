"""CLI commands for redacted vault display."""

from envault.env_redact import redact_env, format_redact_result, count_redacted, RedactError


def cmd_redact(vault_name: str, password: str, show_keys: list[str] | None = None, raw: bool = False) -> dict:
    """Display vault contents with sensitive values redacted.

    Returns:
        dict with redacted env, counts, and optional formatted string
    """
    try:
        redacted = redact_env(vault_name, password, show_keys=show_keys)
    except RedactError as e:
        return {"ok": False, "error": str(e)}

    total = len(redacted)
    n_redacted = count_redacted(redacted)

    result = {
        "ok": True,
        "vault": vault_name,
        "env": redacted,
        "total": total,
        "redacted_count": n_redacted,
        "visible_count": total - n_redacted,
    }

    if not raw:
        result["formatted"] = format_redact_result(redacted)

    return result
