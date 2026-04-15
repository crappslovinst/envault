"""CLI commands for vault health checks."""

from envault.env_health import check_health, format_health_report, HealthError


def cmd_health(vault_name: str, password: str, required_keys: list[str] | None = None) -> dict:
    """
    Run a health check on a vault.

    Returns a dict with keys:
      - ok (bool)
      - report (dict)  – raw report from check_health
      - summary (str)  – formatted human-readable output
      - error (str | None)
    """
    try:
        report = check_health(vault_name, password, required_keys=required_keys)
        return {
            "ok": report["ok"],
            "report": report,
            "summary": format_health_report(report),
            "error": None,
        }
    except HealthError as exc:
        return {
            "ok": False,
            "report": None,
            "summary": "",
            "error": str(exc),
        }
