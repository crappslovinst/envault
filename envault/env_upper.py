from envault.vault_ops import get_env_vars, push_env
from envault.storage import vault_exists


class UpperError(Exception):
    pass


def upper_keys(vault: str, password: str, dry_run: bool = False) -> dict:
    """Convert all keys in a vault to UPPER_CASE."""
    if not vault_exists(vault):
        raise UpperError(f"Vault '{vault}' not found")

    env = get_env_vars(vault, password)
    original = dict(env)
    updated = {k.upper(): v for k, v in env.items()}

    changed = {k for k in updated if k not in original}
    unchanged = len(original) - len(changed)

    if updated != original and not dry_run:
        push_env(vault, password, updated)

    return {
        "vault": vault,
        "total": len(updated),
        "changed": len(changed),
        "unchanged": unchanged,
        "dry_run": dry_run,
        "env": updated,
    }


def format_upper_result(result: dict) -> str:
    lines = [
        f"Vault : {result['vault']}",
        f"Total : {result['total']}",
        f"Changed : {result['changed']}",
        f"Unchanged: {result['unchanged']}",
    ]
    if result["dry_run"]:
        lines.append("(dry run — no changes written)")
    return "\n".join(lines)
