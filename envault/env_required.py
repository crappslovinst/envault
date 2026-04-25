"""Check and enforce required keys in a vault."""

from envault.vault_ops import get_env_vars
from envault.storage import vault_exists


class RequiredError(Exception):
    pass


def check_required(vault_name: str, password: str, required_keys: list[str]) -> dict:
    """Check which required keys are present or missing in a vault."""
    if not vault_exists(vault_name):
        raise RequiredError(f"Vault '{vault_name}' not found")

    env = get_env_vars(vault_name, password)
    present = [k for k in required_keys if k in env]
    missing = [k for k in required_keys if k not in env]

    return {
        "vault": vault_name,
        "required": required_keys,
        "present": present,
        "missing": missing,
        "ok": len(missing) == 0,
    }


def enforce_required(vault_name: str, password: str, required_keys: list[str]) -> dict:
    """Like check_required but raises if any keys are missing."""
    result = check_required(vault_name, password, required_keys)
    if not result["ok"]:
        missing = ", ".join(result["missing"])
        raise RequiredError(
            f"Vault '{vault_name}' is missing required keys: {missing}"
        )
    return result


def format_required_result(result: dict) -> str:
    """Format the result of a required-key check for display."""
    lines = [f"Vault: {result['vault']}"]
    lines.append(f"Required: {len(result['required'])} keys")
    lines.append(f"Present:  {len(result['present'])}")
    lines.append(f"Missing:  {len(result['missing'])}")
    if result["missing"]:
        lines.append("Missing keys:")
        for k in result["missing"]:
            lines.append(f"  - {k}")
    status = "OK" if result["ok"] else "FAIL"
    lines.append(f"Status: {status}")
    return "\n".join(lines)
