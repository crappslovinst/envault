"""CLI commands for importing env vars into a vault."""

from pathlib import Path
from envault.import_env import (
    import_from_dotenv,
    import_from_json,
    import_from_shell,
    ImportError,
)

_IMPORTERS = {
    "dotenv": import_from_dotenv,
    "json": import_from_json,
    "shell": import_from_shell,
}


def cmd_import(
    vault_name: str,
    password: str,
    filepath: str,
    fmt: str = "dotenv",
) -> dict:
    """
    Import env vars from a file into the named vault.

    Args:
        vault_name: Target vault name.
        password:   Encryption password.
        filepath:   Path to the source file.
        fmt:        File format — 'dotenv', 'json', or 'shell'.

    Returns:
        Dict of imported key-value pairs.

    Raises:
        ValueError: Unknown format.
        ImportError: File missing, empty, or malformed.
    """
    if fmt not in _IMPORTERS:
        raise ValueError(
            f"Unknown format '{fmt}'. Choose from: {', '.join(_IMPORTERS)}"
        )
    importer = _IMPORTERS[fmt]
    data = importer(vault_name, password, filepath)
    return {
        "vault": vault_name,
        "format": fmt,
        "source": str(Path(filepath).resolve()),
        "imported_keys": list(data.keys()),
        "count": len(data),
    }
