"""Format/normalize .env file contents stored in a vault."""

from envault.vault_ops import get_env_vars, push_env


class FmtError(Exception):
    pass


def _normalize_key(key: str) -> str:
    return key.strip().upper()


def _normalize_value(value: str) -> str:
    return value.strip()


def format_vault(vault_name: str, password: str, dry_run: bool = False) -> dict:
    """Normalize all keys (uppercase) and strip whitespace from values."""
    try:
        env = get_env_vars(vault_name, password)
    except Exception as e:
        raise FmtError(f"Could not load vault '{vault_name}': {e}") from e

    original = dict(env)
    formatted = {_normalize_key(k): _normalize_value(v) for k, v in env.items()}

    changed_keys = [
        k for k in formatted
        if formatted[k] != original.get(k) or k != k.upper()
    ]
    # also catch keys that changed name (lowercase -> uppercase)
    renamed = [k for k in original if k != _normalize_key(k)]

    if not dry_run and (changed_keys or renamed):
        push_env(vault_name, password, formatted)

    return {
        "vault": vault_name,
        "total_keys": len(formatted),
        "changed": len(set(changed_keys) | set(renamed)),
        "dry_run": dry_run,
        "formatted": formatted,
    }


def format_fmt_result(result: dict) -> str:
    lines = [
        f"Vault   : {result['vault']}",
        f"Keys    : {result['total_keys']}",
        f"Changed : {result['changed']}",
        f"Dry run : {result['dry_run']}",
    ]
    return "\n".join(lines)
