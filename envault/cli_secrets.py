"""CLI commands for secrets scanning."""

from envault.env_secrets import SecretsError, scan_secrets, format_secrets_report


def cmd_scan_secrets(vault_name: str, password: str, raw: bool = False) -> dict:
    """Scan vault for sensitive keys and return report."""
    try:
        report = scan_secrets(vault_name, password)
    except SecretsError as e:
        return {"ok": False, "error": str(e)}

    result = {"ok": True, "report": report}
    if not raw:
        result["formatted"] = format_secrets_report(report)
    return result
