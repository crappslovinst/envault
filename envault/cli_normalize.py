"""CLI command for normalizing vault values."""

from envault.env_normalize import NormalizeError, normalize_vault, format_normalize_result


def cmd_normalize(
    vault_name: str,
    password: str,
    normalize_bools: bool = True,
    dry_run: bool = False,
    raw: bool = False,
) -> dict:
    """Normalize vault values (trim whitespace, standardize booleans)."""
    try:
        result = normalize_vault(
            vault_name,
            password,
            normalize_bools=normalize_bools,
            dry_run=dry_run,
        )
    except NormalizeError as exc:
        return {"ok": False, "error": str(exc)}

    if not raw:
        result["formatted"] = format_normalize_result(result)

    result["ok"] = True
    return result
