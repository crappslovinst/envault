"""CLI operations for the export command."""

from typing import Optional

from envault.export import export_env, export_to_file, SUPPORTED_FORMATS
from envault.vault_ops import get_env_vars


def cmd_export(
    vault_name: str,
    password: str,
    fmt: str = "dotenv",
    output_path: Optional[str] = None,
    prefix: Optional[str] = None,
) -> str:
    """Export a vault's env vars to the given format.

    Args:
        vault_name: Name of the vault to export.
        password: Master password used to decrypt the vault.
        fmt: Output format — 'dotenv', 'shell', or 'json'.
        output_path: If provided, write the output to this file path.
        prefix: Optional key prefix for the exported variables.

    Returns:
        The exported content as a string.

    Raises:
        ValueError: For unsupported formats or missing vaults.
        FileNotFoundError: When the vault does not exist.
    """
    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unknown format '{fmt}'. Supported: {', '.join(SUPPORTED_FORMATS)}"
        )

    env_vars = get_env_vars(vault_name, password)
    content = export_env(env_vars, fmt=fmt, prefix=prefix)

    if output_path:
        export_to_file(env_vars, output_path, fmt=fmt, prefix=prefix)

    return content
