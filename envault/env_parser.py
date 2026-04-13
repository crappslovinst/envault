"""Utilities for parsing and serializing .env file content."""

from typing import Dict, Optional


def parse_env(content: str) -> Dict[str, str]:
    """Parse .env file content into a dictionary.

    Supports:
    - KEY=VALUE pairs
    - Quoted values (single or double)
    - Inline comments (# ...)
    - Blank lines and full-line comments are skipped
    """
    result: Dict[str, str] = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, raw_value = line.partition("=")
        key = key.strip()
        raw_value = raw_value.strip()

        # Strip inline comments (only outside quotes)
        value = _strip_inline_comment(raw_value)

        # Strip surrounding quotes
        if len(value) >= 2 and value[0] in ('"', "'") and value[0] == value[-1]:
            value = value[1:-1]

        if key:
            result[key] = value
    return result


def serialize_env(data: Dict[str, str]) -> str:
    """Serialize a dictionary back to .env file format."""
    lines = []
    for key, value in data.items():
        # Quote value if it contains spaces or special characters
        if any(c in value for c in (" ", "#", "'", '"')):
            escaped = value.replace('"', '\\"')
            lines.append(f'{key}="{escaped}"')
        else:
            lines.append(f"{key}={value}")
    return "\n".join(lines) + ("\n" if lines else "")


def _strip_inline_comment(value: str) -> str:
    """Remove inline comment from a value string, respecting quotes."""
    in_quote: Optional[str] = None
    for i, ch in enumerate(value):
        if ch in ('"', "'") and in_quote is None:
            in_quote = ch
        elif ch == in_quote:
            in_quote = None
        elif ch == "#" and in_quote is None:
            return value[:i].strip()
    return value
