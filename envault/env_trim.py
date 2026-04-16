"""Trim unused or duplicate keys from a vault."""

from envault.vault_ops import get_env_vars, push_env


class TrimError(Exception):
    pass


def find_duplicates(env: dict) -> list:
    """Return keys that appear to be duplicated by case variation."""
    seen = {}
    dupes = []
    for key in env:
        lower = key.lower()
        if lower in seen:
            dupes.append((seen[lower], key))
        else:
            seen[lower] = key
    return dupes


def trim_vault(
    vault_name: str,
    password: str,
    remove_empty: bool = True,
    remove_duplicates: bool = True,
    dry_run: bool = False,
) -> dict:
    """Remove empty values and/or case-duplicate keys from a vault."""
    try:
        env = get_env_vars(vault_name, password)
    except Exception as e:
        raise TrimError(str(e)) from e

    removed_empty = []
    removed_dupes = []
    result = dict(env)

    if remove_empty:
        empty_keys = [k for k, v in result.items() if v.strip() == ""]
        for k in empty_keys:
            del result[k]
            removed_empty.append(k)

    if remove_duplicates:
        dupes = find_duplicates(result)
        for original, duplicate in dupes:
            if duplicate in result:
                del result[duplicate]
                removed_dupes.append((original, duplicate))

    changed = bool(removed_empty or removed_dupes)

    if changed and not dry_run:
        try:
            push_env(vault_name, password, result)
        except Exception as e:
            raise TrimError(f"Failed to save trimmed vault: {e}") from e

    return {
        "vault": vault_name,
        "removed_empty": removed_empty,
        "removed_duplicates": removed_dupes,
        "total_removed": len(removed_empty) + len(removed_dupes),
        "dry_run": dry_run,
        "changed": changed,
    }


def format_trim_result(result: dict) -> str:
    lines = [f"Vault: {result['vault']}"]
    if result["dry_run"]:
        lines.append("(dry run — no changes saved)")
    if result["removed_empty"]:
        lines.append(f"Removed empty keys ({len(result['removed_empty'])}): {', '.join(result['removed_empty'])}")
    if result["removed_duplicates"]:
        pairs = ", ".join(f"{a}↔{b}" for a, b in result["removed_duplicates"])
        lines.append(f"Removed duplicate keys ({len(result['removed_duplicates'])}): {pairs}")
    if not result["changed"]:
        lines.append("Nothing to trim.")
    return "\n".join(lines)
