"""Resolve variable interpolation within a vault (e.g. FOO=${BAR}_suffix)."""

import re
from envault.vault_ops import get_env_vars

REF_PATTERN = re.compile(r"\$\{([^}]+)\}")


class ResolveError(Exception):
    pass


def resolve_vars(vault_name: str, password: str, max_depth: int = 10) -> dict:
    """Return env dict with all ${VAR} references expanded."""
    try:
        env = get_env_vars(vault_name, password)
    except Exception as e:
        raise ResolveError(str(e)) from e

    resolved = dict(env)

    for _ in range(max_depth):
        changed = False
        for key, value in resolved.items():
            new_value = _interpolate(value, resolved)
            if new_value != value:
                resolved[key] = new_value
                changed = True
        if not changed:
            break
    else:
        unresolved = [k for k, v in resolved.items() if REF_PATTERN.search(v)]
        if unresolved:
            raise ResolveError(f"Circular or unresolvable references: {unresolved}")

    return resolved


def _interpolate(value: str, env: dict) -> str:
    def replacer(match):
        ref_key = match.group(1)
        return env.get(ref_key, match.group(0))
    return REF_PATTERN.sub(replacer, value)


def find_references(env: dict) -> dict:
    """Return a map of key -> list of keys it references."""
    refs = {}
    for key, value in env.items():
        found = REF_PATTERN.findall(value)
        if found:
            refs[key] = found
    return refs


def find_undefined_references(env: dict) -> dict:
    """Return a map of key -> list of referenced keys that don't exist in env.

    Useful for detecting typos or missing variables before attempting resolution.
    """
    undefined = {}
    for key, refs in find_references(env).items():
        missing = [ref for ref in refs if ref not in env]
        if missing:
            undefined[key] = missing
    return undefined


def format_resolve_result(resolved: dict, original: dict) -> str:
    lines = []
    for key in sorted(resolved):
        orig = original.get(key, "")
        res = resolved[key]
        if orig != res:
            lines.append(f"  {key}: '{orig}' -> '{res}'")
    if not lines:
        return "No interpolations applied."
    return "Resolved interpolations:\n" + "\n".join(lines)
