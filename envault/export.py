"""Export vault contents to various formats (shell, JSON, dotenv)."""

import json
from typing import Dict, Optional


SUPPORTED_FORMATS = ("dotenv", "shell", "json")


def export_env(
    env_vars: Dict[str, str],
    fmt: str = "dotenv",
    prefix: Optional[str] = None,
) -> str:
    """Serialize env vars to the requested export format.

    Args:
        env_vars: Mapping of key -> value pairs.
        fmt: One of 'dotenv', 'shell', or 'json'.
        prefix: Optional prefix to prepend to every key (shell/dotenv only).

    Returns:
        A string in the requested format.

    Raises:
        ValueError: If *fmt* is not a supported format.
    """
    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported format '{fmt}'. Choose from: {', '.join(SUPPORTED_FORMATS)}"
        )

    if fmt == "json":
        keyed = (
            {f"{prefix}{k}": v for k, v in env_vars.items()} if prefix else env_vars
        )
        return json.dumps(keyed, indent=2)

    lines = []
    for key, value in env_vars.items():
        full_key = f"{prefix}{key}" if prefix else key
        # Wrap value in double-quotes; escape embedded quotes
        escaped = value.replace('"', '\\"')
        if fmt == "shell":
            lines.append(f'export {full_key}="{escaped}"')
        else:  # dotenv
            lines.append(f'{full_key}="{escaped}"')

    return "\n".join(lines)


def export_to_file(env_vars: Dict[str, str], path: str, fmt: str = "dotenv", prefix: Optional[str] = None) -> None:
    """Write exported env vars directly to *path*."""
    content = export_env(env_vars, fmt=fmt, prefix=prefix)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
        if not content.endswith("\n"):
            fh.write("\n")
