"""Generate human-readable diff reports between vault env and a local .env file."""

from envault.vault_ops import get_env_vars
from envault.env_parser import parse_env
from envault.diff import diff_envs, format_diff, has_diff


class ReportError(Exception):
    pass


def generate_report(vault_name: str, password: str, env_file: str) -> dict:
    """Compare a vault's env vars against a local .env file and return a report dict."""
    try:
        vault_vars = get_env_vars(vault_name, password)
    except Exception as e:
        raise ReportError(f"Failed to load vault '{vault_name}': {e}") from e

    try:
        with open(env_file, "r") as f:
            local_vars = parse_env(f.read())
    except FileNotFoundError:
        raise ReportError(f"Local env file not found: {env_file}")
    except Exception as e:
        raise ReportError(f"Failed to read env file '{env_file}': {e}") from e

    diff = diff_envs(vault_vars, local_vars)
    lines = format_diff(diff)

    return {
        "vault": vault_name,
        "env_file": env_file,
        "has_diff": has_diff(diff),
        "added": [e["key"] for e in diff if e["status"] == "added"],
        "removed": [e["key"] for e in diff if e["status"] == "removed"],
        "changed": [e["key"] for e in diff if e["status"] == "changed"],
        "unchanged": [e["key"] for e in diff if e["status"] == "unchanged"],
        "formatted": lines,
    }


def save_report(report: dict, output_file: str) -> None:
    """Write a formatted diff report to a file."""
    try:
        with open(output_file, "w") as f:
            f.write(f"# Envault Diff Report\n")
            f.write(f"# Vault : {report['vault']}\n")
            f.write(f"# File  : {report['env_file']}\n")
            f.write(f"# Diff  : {'yes' if report['has_diff'] else 'no'}\n\n")
            for line in report["formatted"]:
                f.write(line + "\n")
    except Exception as e:
        raise ReportError(f"Failed to write report to '{output_file}': {e}") from e
