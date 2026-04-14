"""Pin management: lock a vault to a specific snapshot version."""

from __future__ import annotations

from envault.storage import load_vault, save_vault, vault_exists


class PinError(Exception):
    pass


def _get_pins(data: dict) -> dict:
    return data.get("__pins__", {})


def pin_vault(vault_name: str, password: str, snapshot_id: str) -> dict:
    """Pin a vault to a specific snapshot ID."""
    if not vault_exists(vault_name):
        raise PinError(f"Vault '{vault_name}' does not exist.")

    data = load_vault(vault_name, password)
    pins = _get_pins(data)
    pins["pinned_snapshot"] = snapshot_id
    data["__pins__"] = pins
    save_vault(vault_name, data, password)

    return {"vault
ed_snapshot": snapshot_id, "status": "pinned"}


def unpin_vault(vault_name: str, password: str) -> dict:
    """Remove the pin from a vault."""
    if not vault_exists(vault_name):
        raise PinError(f"Vault '{vault_name}' does not exist.")

    data = load_vault(vault_name, password)
    pins = _get_pins(data)

    if "pinned_snapshot" not in pins:
        raise PinError(f"Vault '{vault_name}' is not pinned.")

    del pins["pinned_snapshot"]
    data["__pins__"] = pins
    save_vault(vault_name, data, password)

    return {"vault": vault_name, "status": "unpinned"}


def get_pin(vault_name: str, password: str) -> dict:
    """Return the current pin info for a vault."""
    if not vault_exists(vault_name):
        raise PinError(f"Vault '{vault_name}' does not exist.")

    data = load_vault(vault_name, password)
    pins = _get_pins(data)
    snapshot_id = pins.get("pinned_snapshot")

    return {
        "vault": vault_name,
        "pinned": snapshot_id is not None,
        "pinned_snapshot": snapshot_id,
    }


def is_pinned(vault_name: str, password: str) -> bool:
    """Return True if the vault is currently pinned."""
    return get_pin(vault_name, password)["pinned"]
