"""Pin a vault to a specific schema/version string for compatibility checks."""

from envault.storage import load_vault, save_vault, vault_exists

PIN_VERSION_KEY = "__pin_version__"


class PinVersionError(Exception):
    pass


def set_version_pin(vault_name: str, password: str, version: str) -> dict:
    """Attach a version pin to the vault metadata."""
    if not vault_exists(vault_name):
        raise PinVersionError(f"Vault '{vault_name}' not found.")
    if not version or not version.strip():
        raise PinVersionError("Version string must not be empty.")
    data = load_vault(vault_name, password)
    data[PIN_VERSION_KEY] = version.strip()
    save_vault(vault_name, password, data)
    return {"vault": vault_name, "version": version.strip(), "status": "pinned"}


def get_version_pin(vault_name: str, password: str) -> dict:
    """Return the current version pin for a vault, or None if not set."""
    if not vault_exists(vault_name):
        raise PinVersionError(f"Vault '{vault_name}' not found.")
    data = load_vault(vault_name, password)
    version = data.get(PIN_VERSION_KEY)
    return {"vault": vault_name, "version": version, "pinned": version is not None}


def clear_version_pin(vault_name: str, password: str) -> dict:
    """Remove the version pin from a vault."""
    if not vault_exists(vault_name):
        raise PinVersionError(f"Vault '{vault_name}' not found.")
    data = load_vault(vault_name, password)
    removed = PIN_VERSION_KEY in data
    data.pop(PIN_VERSION_KEY, None)
    save_vault(vault_name, password, data)
    return {"vault": vault_name, "cleared": removed}


def check_version_compatible(vault_name: str, password: str, required: str) -> dict:
    """Check whether the vault's pinned version matches the required version."""
    info = get_version_pin(vault_name, password)
    pinned = info.get("version")
    compatible = pinned == required if pinned is not None else False
    return {
        "vault": vault_name,
        "pinned_version": pinned,
        "required_version": required,
        "compatible": compatible,
    }


def format_version_info(info: dict) -> str:
    vault = info.get("vault", "")
    version = info.get("version")
    if version:
        return f"[{vault}] pinned version: {version}"
    return f"[{vault}] no version pin set"
