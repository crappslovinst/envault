"""Template support for envault — generate .env templates from vault data."""

from typing import Optional
from envault.vault_ops import get_env_vars


class TemplateError(Exception):
    pass


def generate_template(
    vault_name: str,
    password: str,
    placeholder: str = "",
    include_values: bool = False,
    prefix_filter: Optional[str] = None,
) -> str:
    """Generate a .env template from a vault, optionally blanking out values.

    Args:
        vault_name: Name of the vault to read from.
        password: Vault password.
        placeholder: Value to use in place of real values (default: empty string).
        include_values: If True, keep actual values instead of replacing them.
        prefix_filter: If set, only include keys starting with this prefix.

    Returns:
        A string in .env format suitable for use as a template.
    """
    try:
        env_vars = get_env_vars(vault_name, password)
    except Exception as exc:
        raise TemplateError(f"Could not read vault '{vault_name}': {exc}") from exc

    lines = [f"# Template generated from vault: {vault_name}", ""]

    for key, value in sorted(env_vars.items()):
        if prefix_filter and not key.startswith(prefix_filter):
            continue
        display_value = value if include_values else placeholder
        lines.append(f"{key}={display_value}")

    return "\n".join(lines) + "\n"


def save_template(content: str, output_path: str) -> None:
    """Write template content to a file."""
    try:
        with open(output_path, "w", encoding="utf-8") as fh:
            fh.write(content)
    except OSError as exc:
        raise TemplateError(f"Could not write template to '{output_path}': {exc}") from exc
