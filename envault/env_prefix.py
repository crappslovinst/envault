from envault.vault_ops import get_env_vars, push_env


class PrefixError(Exception):
    pass


def add_prefix(vault: str, password: str, prefix: str, dry_run: bool = False) -> dict:
    """Add a prefix to all keys in a vault."""
    env = get_env_vars(vault, password)
    if not env:
        raise PrefixError(f"Vault '{vault}' is empty or not found")

    updated = {}
    skipped = []
    renamed = []

    for key, value in env.items():
        if key.startswith(prefix):
            updated[key] = value
            skipped.append(key)
        else:
            new_key = f"{prefix}{key}"
            updated[new_key] = value
            renamed.append((key, new_key))

    if not dry_run and renamed:
        push_env(vault, password, updated)

    return {
        "vault": vault,
        "prefix": prefix,
        "renamed": renamed,
        "skipped": skipped,
        "dry_run": dry_run,
        "total_renamed": len(renamed),
    }


def remove_prefix(vault: str, password: str, prefix: str, dry_run: bool = False) -> dict:
    """Remove a prefix from all matching keys in a vault."""
    env = get_env_vars(vault, password)
    if not env:
        raise PrefixError(f"Vault '{vault}' is empty or not found")

    updated = {}
    skipped = []
    renamed = []

    for key, value in env.items():
        if key.startswith(prefix):
            new_key = key[len(prefix):]
            if not new_key:
                skipped.append(key)
                updated[key] = value
            else:
                updated[new_key] = value
                renamed.append((key, new_key))
        else:
            updated[key] = value
            skipped.append(key)

    if not dry_run and renamed:
        push_env(vault, password, updated)

    return {
        "vault": vault,
        "prefix": prefix,
        "renamed": renamed,
        "skipped": skipped,
        "dry_run": dry_run,
        "total_renamed": len(renamed),
    }


def format_prefix_result(result: dict) -> str:
    lines = [
        f"Vault : {result['vault']}",
        f"Prefix: {result['prefix']}",
        f"Renamed : {result['total_renamed']} key(s)",
        f"Skipped : {len(result['skipped'])} key(s)",
    ]
    if result["dry_run"]:
        lines.append("(dry run — no changes saved)")
    return "\n".join(lines)
