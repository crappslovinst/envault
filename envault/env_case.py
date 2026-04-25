"""env_case.py — detect and report key casing inconsistencies in a vault."""

from __future__ import annotations

from typing import Dict, List

from envault.vault_ops import get_env_vars
from envault.storage import vault_exists


class CaseError(Exception):
    pass


_STYLES = ("upper", "lower", "mixed", "unknown")


def _classify(key: str) -> str:
    if key == key.upper():
        return "upper"
    if key == key.lower():
        return "lower"
    if key[0].isupper() or "_" in key:
        return "mixed"
    return "unknown"


def analyze_case(vault_name: str, password: str) -> Dict:
    """Return a breakdown of key casing styles in the vault."""
    if not vault_exists(vault_name):
        raise CaseError(f"Vault '{vault_name}' not found.")

    env = get_env_vars(vault_name, password)

    groups: Dict[str, List[str]] = {s: [] for s in _STYLES}
    for key in env:
        groups[_classify(key)].append(key)

    dominant = max(groups, key=lambda s: len(groups[s]))
    inconsistent = [
        key
        for style, keys in groups.items()
        if style != dominant
        for key in keys
    ]

    return {
        "vault": vault_name,
        "total": len(env),
        "dominant_style": dominant,
        "groups": {s: sorted(keys) for s, keys in groups.items()},
        "inconsistent": sorted(inconsistent),
        "inconsistent_count": len(inconsistent),
    }


def format_case_result(result: Dict) -> str:
    lines = [
        f"Vault : {result['vault']}",
        f"Total keys     : {result['total']}",
        f"Dominant style : {result['dominant_style']}",
        f"Inconsistent   : {result['inconsistent_count']}",
    ]
    if result["inconsistent"]:
        lines.append("Offending keys:")
        for k in result["inconsistent"]:
            lines.append(f"  - {k}")
    return "\n".join(lines)
