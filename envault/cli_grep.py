"""CLI command for grep feature."""

from envault.env_grep import grep_vault, format_grep_result, GrepError


def cmd_grep(
    vault_name: str,
    password: str,
    pattern: str,
    *,
    keys_only: bool = False,
    values_only: bool = False,
    case_sensitive: bool = False,
    raw: bool = False,
) -> dict:
    """Run grep against a vault and return result dict (with optional formatted string)."""
    search_keys = not values_only
    search_values = not keys_only

    try:
        result = grep_vault(
            vault_name,
            password,
            pattern,
            search_keys=search_keys,
            search_values=search_values,
            case_sensitive=case_sensitive,
        )
    except GrepError as e:
        return {"ok": False, "error": str(e)}

    if not raw:
        result["formatted"] = format_grep_result(result)
    return {"ok": True, **result}
