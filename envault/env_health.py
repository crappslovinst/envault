"""Vault health check: summarizes age, TTL, lint, and missing keys."""

from datetime import datetime, timezone
from envault.vault_ops import get_env_vars
from envault.storage import vault_exists
from envault.ttl import get_ttl, is_expired
from envault.env_lint import lint_vault


class HealthError(Exception):
    pass


def check_health(vault_name: str, password: str, required_keys: list[str] | None = None) -> dict:
    """Run a full health check on a vault and return a structured report."""
    if not vault_exists(vault_name):
        raise HealthError(f"Vault '{vault_name}' not found")

    report = {
        "vault": vault_name,
        "ok": True,
        "issues": [],
        "ttl": None,
        "expired": False,
        "lint": None,
        "missing_keys": [],
        "key_count": 0,
    }

    # Key count
    env_vars = get_env_vars(vault_name, password)
    report["key_count"] = len(env_vars)

    # TTL check
    ttl_info = get_ttl(vault_name)
    if ttl_info:
        report["ttl"] = ttl_info
        expired = is_expired(vault_name)
        report["expired"] = expired
        if expired:
            report["ok"] = False
            report["issues"].append("vault has expired (TTL exceeded)")

    # Lint check
    lint_result = lint_vault(vault_name, password)
    report["lint"] = lint_result
    if lint_result.get("issue_count", 0) > 0:
        report["ok"] = False
        report["issues"].append(f"{lint_result['issue_count']} lint issue(s) found")

    # Missing required keys
    if required_keys:
        missing = [k for k in required_keys if k not in env_vars]
        report["missing_keys"] = missing
        if missing:
            report["ok"] = False
            report["issues"].append(f"missing required keys: {', '.join(missing)}")

    return report


def format_health_report(report: dict) -> str:
    """Return a human-readable health report string."""
    lines = [
        f"Vault : {report['vault']}",
        f"Status: {'OK' if report['ok'] else 'UNHEALTHY'}",
        f"Keys  : {report['key_count']}",
    ]
    if report["ttl"]:
        lines.append(f"TTL   : expires_at={report['ttl'].get('expires_at')} expired={report['expired']}")
    if report["issues"]:
        lines.append("Issues:")
        for issue in report["issues"]:
            lines.append(f"  - {issue}")
    return "\n".join(lines)
