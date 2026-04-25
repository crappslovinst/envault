"""CLI commands for required-key enforcement."""

from envault.env_required import (
    RequiredError,
    check_required,
    enforce_required,
    format_required_result,
)


def cmd_check_required(
    vault_name: str,
    password: str,
    required_keys: list[str],
    *,
    enforce: bool = False,
    raw: bool = False,
) -> dict:
    """Check (or enforce) that a vault contains all required keys."""
    try:
        if enforce:
            result = enforce_required(vault_name, password, required_keys)
        else:
            result = check_required(vault_name, password, required_keys)
    except RequiredError as exc:
        return {"ok": False, "error": str(exc)}

    if not raw:
        result["formatted"] = format_required_result(result)
    return result
