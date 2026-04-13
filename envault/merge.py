"""Utilities for merging two sets of env vars with conflict resolution strategies."""

from typing import Dict, Literal

MergeStrategy = Literal["ours", "theirs", "interactive"]


def merge_envs(
    base: Dict[str, str],
    incoming: Dict[str, str],
    strategy: MergeStrategy = "theirs",
) -> Dict[str, str]:
    """Merge two env dicts using the given strategy.

    - 'ours':   keep base values on conflict
    - 'theirs': use incoming values on conflict
    - 'interactive': raises NotImplementedError (handled at CLI layer)
    """
    if strategy == "interactive":
        raise NotImplementedError(
            "Interactive merge must be handled at the CLI layer."
        )

    merged = dict(base)

    for key, value in incoming.items():
        if key not in merged:
            merged[key] = value
        else:
            if strategy == "theirs":
                merged[key] = value
            # strategy == "ours": keep existing, do nothing

    return merged


def get_conflicts(base: Dict[str, str], incoming: Dict[str, str]) -> Dict[str, tuple]:
    """Return keys that exist in both dicts but with different values.

    Returns a dict of {key: (base_value, incoming_value)}.
    """
    conflicts = {}
    for key in base:
        if key in incoming and base[key] != incoming[key]:
            conflicts[key] = (base[key], incoming[key])
    return conflicts


def resolve_interactive(
    base: Dict[str, str],
    incoming: Dict[str, str],
    resolutions: Dict[str, str],
) -> Dict[str, str]:
    """Apply manual resolutions to a merge.

    `resolutions` maps conflicting keys to their chosen values.
    Keys not in resolutions fall back to 'theirs' strategy.
    """
    merged = merge_envs(base, incoming, strategy="theirs")
    for key, value in resolutions.items():
        merged[key] = value
    return merged
