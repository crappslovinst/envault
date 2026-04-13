"""Utilities for diffing two sets of env vars."""

from typing import Any


def diff_envs(local: dict[str, str], remote: dict[str, str]) -> dict[str, Any]:
    """Compare local and remote env dicts.

    Returns a dict with:
        - added:   keys in remote but not local
        - removed: keys in local but not remote
        - changed: keys in both but with different values
        - unchanged: keys with identical values
    """
    local_keys = set(local.keys())
    remote_keys = set(remote.keys())

    added = {k: remote[k] for k in remote_keys - local_keys}
    removed = {k: local[k] for k in local_keys - remote_keys}
    changed = {
        k: {"local": local[k], "remote": remote[k]}
        for k in local_keys & remote_keys
        if local[k] != remote[k]
    }
    unchanged = {
        k: local[k]
        for k in local_keys & remote_keys
        if local[k] == remote[k]
    }

    return {
        "added": added,
        "removed": removed,
        "changed": changed,
        "unchanged": unchanged,
    }


def has_diff(result: dict[str, Any]) -> bool:
    """Return True if there are any differences."""
    return bool(result["added"] or result["removed"] or result["changed"])


def format_diff(result: dict[str, Any]) -> str:
    """Return a human-readable diff summary."""
    lines = []

    for key, value in sorted(result["added"].items()):
        lines.append(f"  + {key}={value}")

    for key, value in sorted(result["removed"].items()):
        lines.append(f"  - {key}={value}")

    for key, vals in sorted(result["changed"].items()):
        lines.append(f"  ~ {key}: {vals['local']!r} -> {vals['remote']!r}")

    if not lines:
        return "  (no differences)"

    return "\n".join(lines)
