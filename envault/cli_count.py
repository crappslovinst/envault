"""CLI command for env-count feature."""

from envault.env_count import CountError, count_keys, format_count_result


def cmd_count(vault_name: str, password: str, raw: bool = False) -> dict:
    """Return key count summary for a vault.

    Args:
        vault_name: Name of the vault.
        password: Vault password.
        raw: If True, skip formatted string in result.

    Returns:
        dict with count data and optional 'formatted' key.
    """
    try:
        result = count_keys(vault_name, password)
    except CountError as e:
        return {"ok": False, "error": str(e)}

    out = {"ok": True, **result}
    if not raw:
        out["formatted"] = format_count_result(result)
    return out
