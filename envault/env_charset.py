"""Charset analysis for vault values — detects non-ASCII, control chars, etc."""

import unicodedata
from envault.vault_ops import get_env_vars
from envault.storage import vault_exists


class CharsetError(Exception):
    pass


_CONTROL_CATEGORIES = {"Cc", "Cf", "Cs"}


def _classify_value(value: str) -> dict:
    has_non_ascii = any(ord(c) > 127 for c in value)
    control_chars = [
        c for c in value if unicodedata.category(c) in _CONTROL_CATEGORIES
    ]
    has_whitespace_only = value.strip() == "" and len(value) > 0
    return {
        "non_ascii": has_non_ascii,
        "control_chars": control_chars,
        "whitespace_only": has_whitespace_only,
        "length": len(value),
    }


def analyze_charset(
    vault_name: str,
    password: str,
    flag_non_ascii: bool = True,
    flag_control: bool = True,
) -> dict:
    if not vault_exists(vault_name):
        raise CharsetError(f"Vault '{vault_name}' not found.")

    env = get_env_vars(vault_name, password)
    flagged = []
    clean = []

    for key, value in env.items():
        info = _classify_value(value)
        reasons = []
        if flag_non_ascii and info["non_ascii"]:
            reasons.append("non_ascii")
        if flag_control and info["control_chars"]:
            reasons.append("control_chars")
        if info["whitespace_only"]:
            reasons.append("whitespace_only")

        if reasons:
            flagged.append({"key": key, "value": value, "reasons": reasons})
        else:
            clean.append(key)

    return {
        "vault": vault_name,
        "total": len(env),
        "flagged": flagged,
        "flagged_count": len(flagged),
        "clean_count": len(clean),
    }


def format_charset_result(result: dict) -> str:
    lines = [
        f"Vault : {result['vault']}",
        f"Total : {result['total']}",
        f"Clean : {result['clean_count']}",
        f"Flagged: {result['flagged_count']}",
    ]
    if result["flagged"]:
        lines.append("")
        lines.append("Flagged keys:")
        for entry in result["flagged"]:
            reasons = ", ".join(entry["reasons"])
            lines.append(f"  {entry['key']}: [{reasons}]")
    return "\n".join(lines)
