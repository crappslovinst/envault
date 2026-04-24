"""Read-only mode for vaults — prevent accidental writes."""

from envault.storage import load_vault, save_vault, vault_exists


class ReadonlyError(Exception):
    pass


def _get_meta(vault_name: str, password: str) -> dict:
    data = load_vault(vault_name, password)
    return data if isinstance(data, dict) else {"__env__": data}


def set_readonly(vault_name: str, password: str, readonly: bool = True) -> dict:
    """Enable or disable read-only mode on a vault."""
    if not vault_exists(vault_name):
        raise ReadonlyError(f"Vault '{vault_name}' not found.")

    data = _get_meta(vault_name, password)
    meta = data.get("__meta__", {})
    meta["readonly"] = readonly
    data["__meta__"] = meta
    save_vault(vault_name, password, data)

    state = "enabled" if readonly else "disabled"
    return {"vault": vault_name, "readonly": readonly, "status": f"Read-only {state}"}


def get_readonly(vault_name: str, password: str) -> dict:
    """Return the current read-only state of a vault."""
    if not vault_exists(vault_name):
        raise ReadonlyError(f"Vault '{vault_name}' not found.")

    data = _get_meta(vault_name, password)
    meta = data.get("__meta__", {})
    readonly = meta.get("readonly", False)
    return {"vault": vault_name, "readonly": readonly}


def assert_writable(vault_name: str, password: str) -> None:
    """Raise ReadonlyError if the vault is in read-only mode."""
    info = get_readonly(vault_name, password)
    if info["readonly"]:
        raise ReadonlyError(
            f"Vault '{vault_name}' is read-only. Disable read-only mode before making changes."
        )


def format_readonly_info(info: dict) -> str:
    state = "ON (write-protected)" if info["readonly"] else "OFF (writable)"
    return f"Vault : {info['vault']}\nRead-only: {state}"
