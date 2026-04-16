"""Detect and resolve placeholder values in vaults."""

from envault.vault_ops import get_env_vars

DEFAULT_PATTERNS = [
    "CHANGE_ME",
    "TODO",
    "PLACEHOLDER",
    "YOUR_",
    "<",
    ">",
]


class PlaceholderError(Exception):
    pass


def find_placeholders(vault_name: str, password: str, patterns: list[str] | None = None) -> dict:
    """Return keys whose values look like unresolved placeholders."""
    patterns = patterns or DEFAULT_PATTERNS
    try:
        env = get_env_vars(vault_name, password)
    except Exception as e:
        raise PlaceholderError(str(e)) from e

    hits = {}
    for key, value in env.items():
        for pat in patterns:
            if pat.upper() in value.upper():
                hits[key] = value
                break
    return hits


def replace_placeholders(vault_name: str, password: str, replacements: dict[str, str]) -> dict:
    """Given a mapping of key->new_value, push updates back to the vault."""
    from envault.vault_ops import push_env

    try:
        current = get_env_vars(vault_name, password)
    except Exception as e:
        raise PlaceholderError(str(e)) from e

    updated = {**current, **replacements}
    push_env(vault_name, password, updated)
    return {"vault": vault_name, "replaced": list(replacements.keys()), "total": len(replacements)}


def format_placeholder_report(hits: dict) -> str:
    if not hits:
        return "No placeholders found."
    lines = ["Unresolved placeholders:"]
    for key, val in hits.items():
        lines.append(f"  {key} = {val!r}")
    return "\n".join(lines)
