"""Lint .env files for common issues like duplicate keys, suspicious values, etc."""

from typing import Optional
from envault.vault_ops import get_env_vars


class LintError(Exception):
    pass


LINT_RULES = [
    "duplicate_keys",
    "empty_values",
    "whitespace_in_keys",
    "keys_not_uppercase",
    "suspicious_placeholders",
]

SUSPICIOUS_PLACEHOLDERS = {"TODO", "FIXME", "CHANGEME", "YOUR_", "<", ">"}


def lint_vault(vault_name: str, password: str, rules: Optional[list] = None) -> dict:
    """Run lint checks on a vault's env vars. Returns a dict with findings."""
    try:
        env = get_env_vars(vault_name, password)
    except Exception as e:
        raise LintError(f"Could not load vault '{vault_name}': {e}") from e

    active_rules = rules or LINT_RULES
    findings = {rule: [] for rule in active_rules}

    seen_keys = {}
    for i, (key, value) in enumerate(env.items()):
        if "duplicate_keys" in active_rules:
            lower = key.lower()
            if lower in seen_keys:
                findings["duplicate_keys"].append(
                    {"key": key, "first_seen": seen_keys[lower]}
                )
            else:
                seen_keys[lower] = key

        if "empty_values" in active_rules and value.strip() == "":
            findings["empty_values"].append({"key": key})

        if "whitespace_in_keys" in active_rules and key != key.strip():
            findings["whitespace_in_keys"].append({"key": repr(key)})

        if "keys_not_uppercase" in active_rules and key != key.upper():
            findings["keys_not_uppercase"].append({"key": key, "suggested": key.upper()})

        if "suspicious_placeholders" in active_rules:
            for placeholder in SUSPICIOUS_PLACEHOLDERS:
                if placeholder in value:
                    findings["suspicious_placeholders"].append(
                        {"key": key, "matched": placeholder}
                    )
                    break

    total = sum(len(v) for v in findings.values())
    return {
        "vault": vault_name,
        "total_issues": total,
        "findings": findings,
        "passed": total == 0,
    }


def format_lint_result(result: dict) -> str:
    """Return a human-readable summary of lint results."""
    lines = [f"Lint results for vault '{result['vault']}':"]
    if result["passed"]:
        lines.append("  ✓ No issues found.")
        return "\n".join(lines)
    for rule, issues in result["findings"].items():
        iff"  [{rule}] ({len(issues)} issue(s)):")
            for issue in issues:
                lines.append(f"    - {issue}")
    lines.append(f"  Total issues: {result['total_issues']}")
    return "\n".join(lines)
