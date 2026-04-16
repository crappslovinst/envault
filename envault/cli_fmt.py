"""CLI commands for vault formatting."""

from envault.env_fmt import FmtError, format_vault, format_fmt_result


def cmd_fmt(vault_name: str, password: str, dry_run: bool = False, raw: bool = False) -> dict:
    """Normalize keys and values in a vault.

    Args:
        vault_name: Target vault.
        password: Vault password.
        dry_run: Preview changes without saving.
        raw: If True, skip formatted string in result.

    Returns:
        Result dict, optionally with 'formatted_output' key.
    """
    try:
        result = format_vault(vault_name, password, dry_run=dry_run)
    except FmtError as e:
        return {"ok": False, "error": str(e)}

    result["ok"] = True
    if not raw:
        result["formatted_output"] = format_fmt_result(result)
    return result
