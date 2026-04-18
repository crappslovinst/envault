"""Generate a .env.sample file from a vault, blanking out sensitive values."""

from envault.vault_ops import get_env_vars
from envault.env_secrets import _is_sensitive


class SampleError(Exception):
    pass


def generate_sample(
    vault_name: str,
    password: str,
    placeholder: str = "",
    include_values: bool = False,
    mask_sensitive: bool = True,
) -> dict:
    """Return a dict suitable for a .env.sample file."""
    try:
        env = get_env_vars(vault_name, password)
    except Exception as e:
        raise SampleError(str(e)) from e

    sample = {}
    for key, value in env.items():
        if include_values:
            sample[key] = value
        elif mask_sensitive and _is_sensitive(key):
            sample[key] = placeholder
        else:
            sample[key] = value if not mask_sensitive else placeholder

    return {
        "vault": vault_name,
        "total": len(sample),
        "masked": sum(1 for v in sample.values() if v == placeholder),
        "sample": sample,
    }


def save_sample(result: dict, path: str) -> str:
    """Write sample dict to a .env.sample file and return the path."""
    lines = []
    for key, value in result["sample"].items():
        lines.append(f"{key}={value}")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    return path


def format_sample_result(result: dict) -> str:
    lines = [
        f"Vault   : {result['vault']}",
        f"Total   : {result['total']}",
        f"Masked  : {result['masked']}",
        "",
    ]
    for key, value in result["sample"].items():
        display = value if value else "<blank>"
        lines.append(f"  {key}={display}")
    return "\n".join(lines)
