"""Sort vault keys alphabetically or by custom order."""

from envault.vault_ops import get_env_vars, push_env
from envault.storage import vault_exists


class SortError(Exception):
    pass


def sort_vault(
    vault: str,
    password: str,
    reverse: bool = False,
    group_by_prefix: bool = False,
    dry_run: bool = False,
) -> dict:
    if not vault_exists(vault):
        raise SortError(f"Vault '{vault}' not found")

    env = get_env_vars(vault, password)

    if group_by_prefix:
        sorted_env = _sort_by_prefix(env, reverse=reverse)
    else:
        sorted_env = dict(sorted(env.items(), key=lambda x: x[0], reverse=reverse))

    changed = list(env.keys()) != list(sorted_env.keys())

    if changed and not dry_run:
        push_env(vault, password, sorted_env)

    return {
        "vault": vault,
        "total_keys": len(sorted_env),
        "changed": changed,
        "dry_run": dry_run,
        "order": "desc" if reverse else "asc",
        "group_by_prefix": group_by_prefix,
        "keys": list(sorted_env.keys()),
        "env": sorted_env,
    }


def _sort_by_prefix(env: dict, reverse: bool = False) -> dict:
    groups: dict[str, list] = {}
    no_prefix = []

    for key in env:
        if "_" in key:
            prefix = key.split("_")[0]
            groups.setdefault(prefix, []).append(key)
        else:
            no_prefix.append(key)

    sorted_keys = []
    for prefix in sorted(groups.keys(), reverse=reverse):
        sorted_keys.extend(sorted(groups[prefix], reverse=reverse))
    sorted_keys.extend(sorted(no_prefix, reverse=reverse))

    return {k: env[k] for k in sorted_keys}


def format_sort_result(result: dict) -> str:
    lines = [
        f"Vault : {result['vault']}",
        f"Keys  : {result['total_keys']}",
        f"Order : {result['order']}",
        f"Grouped: {result['group_by_prefix']}",
        f"Changed: {result['changed']}",
        f"Dry run: {result['dry_run']}",
    ]
    return "\n".join(lines)
