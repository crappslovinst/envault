"""CLI commands for vault status."""

from envault.env_status import StatusError, get_status, format_status


def cmd_status(vault_name: str, password: str, fmt: str = "text") -> dict:
    """
    Return status info for a vault.

    Args:
        vault_name: name of the vault
        password: vault password (needed for tag decryption)
        fmt: 'text' returns formatted string in result, 'raw' returns raw dict

    Returns:
        dict with 'ok', 'status', and optionally 'formatted'
    """
    try:
        status = get_status(vault_name, password)
    except StatusError as e:
        return {"ok": False, "error": str(e)}

    result = {"ok": True, "status": status}
    if fmt == "text":
        result["formatted"] = format_status(status)
    return result
