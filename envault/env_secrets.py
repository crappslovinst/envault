"""Detect and report potentially sensitive keys in a vault."""

from envault.vault_ops import get_env_vars

SECRET_PATTERNS = [
    "password", "passwd", "secret", "token", "api_key", "apikey",
    "private_key", "auth", "credential", "access_key", "signing",
    "encryption", "cert", "private", "passphrase",
]


class SecretsError(Exception):
    pass


def _is_sensitive(key: str) -> bool:
    lower = key.lower()
    return any(pat in lower for pat in SECRET_PATTERNS)


def scan_secrets(vault_name: str, password: str) -> dict:
    """Scan a vault and return a report of sensitive keys."""
    try:
        env = get_env_vars(vault_name, password)
    except Exception as e:
        raise SecretsError(f"Could not load vault '{vault_name}': {e}") from e

    sensitive = []
    safe = []

    for key in env:
        if _is_sensitive(key):
            sensitive.append(key)
        else:
            safe.append(key)

    return {
        "vault": vault_name,
        "total": len(env),
        "sensitive_count": len(sensitive),
        "safe_count": len(safe),
        "sensitive_keys": sorted(sensitive),
        "safe_keys": sorted(safe),
    }


def format_secrets_report(report: dict) -> str:
    lines = [
        f"Vault: {report['vault']}",
        f"Total keys: {report['total']}",
        f"Sensitive: {report['sensitive_count']}  Safe: {report['safe_count']}",
    ]
    if report["sensitive_keys"]:
        lines.append("Sensitive keys:")
        for k in report["sensitive_keys"]:
            lines.append(f"  ⚠  {k}")
    else:
        lines.append("No sensitive keys detected.")
    return "\n".join(lines)
