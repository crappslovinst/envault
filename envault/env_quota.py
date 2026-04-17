from envault.vault_ops import get_env_vars
from envault.storage import vault_exists


class QuotaError(Exception):
    pass


DEFAULT_MAX_KEYS = 100
DEFAULT_MAX_VALUE_LENGTH = 1024


def check_quota(vault_name: str, password: str, max_keys: int = DEFAULT_MAX_KEYS, max_value_length: int = DEFAULT_MAX_VALUE_LENGTH) -> dict:
    if not vault_exists(vault_name):
        raise QuotaError(f"Vault '{vault_name}' not found")

    env = get_env_vars(vault_name, password)
    violations = []

    if len(env) > max_keys:
        violations.append({
            "type": "too_many_keys",
            "detail": f"{len(env)} keys exceeds limit of {max_keys}"
        })

    long_values = [
        {"key": k, "length": len(v)}
        for k, v in env.items()
        if len(v) > max_value_length
    ]
    for lv in long_values:
        violations.append({
            "type": "value_too_long",
            "detail": f"Key '{lv['key']}' value length {lv['length']} exceeds limit of {max_value_length}"
        })

    return {
        "vault": vault_name,
        "total_keys": len(env),
        "max_keys": max_keys,
        "max_value_length": max_value_length,
        "violations": violations,
        "ok": len(violations) == 0,
    }


def format_quota_result(result: dict) -> str:
    lines = [
        f"Vault : {result['vault']}",
        f"Keys  : {result['total_keys']} / {result['max_keys']}",
    ]
    if result["ok"]:
        lines.append("Status: OK — within quota")
    else:
        lines.append(f"Status: EXCEEDED — {len(result['violations'])} violation(s)")
        for v in result["violations"]:
            lines.append(f"  [{v['type']}] {v['detail']}")
    return "\n".join(lines)
