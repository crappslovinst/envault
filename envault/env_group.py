"""Group management for vaults — organize vaults into named groups."""

from envault.storage import load_vault, save_vault, vault_exists

GROUPS_KEY = "__groups__"
META_VAULT = "__envault_meta__"


class GroupError(Exception):
    pass


def _get_groups(password: str) -> dict:
    if not vault_exists(META_VAULT):
        return {}
    data = load_vault(META_VAULT, password)
    return data.get(GROUPS_KEY, {})


def _save_groups(groups: dict, password: str) -> None:
    data = {}
    if vault_exists(META_VAULT):
        data = load_vault(META_VAULT, password)
    data[GROUPS_KEY] = groups
    save_vault(META_VAULT, data, password)


def add_to_group(vault_name: str, group: str, password: str) -> list:
    """Add a vault to a group. Returns updated member list."""
    groups = _get_groups(password)
    members = groups.get(group, [])
    if vault_name not in members:
        members.append(vault_name)
    groups[group] = members
    _save_groups(groups, password)
    return members


def remove_from_group(vault_name: str, group: str, password: str) -> list:
    """Remove a vault from a group. Returns updated member list."""
    groups = _get_groups(password)
    members = groups.get(group, [])
    if vault_name not in members:
        raise GroupError(f"Vault '{vault_name}' is not in group '{group}'")
    members = [m for m in members if m != vault_name]
    groups[group] = members
    _save_groups(groups, password)
    return members


def list_groups(password: str) -> dict:
    """Return all groups and their members."""
    return _get_groups(password)


def get_group_members(group: str, password: str) -> list:
    """Return members of a specific group."""
    groups = _get_groups(password)
    if group not in groups:
        raise GroupError(f"Group '{group}' does not exist")
    return groups[group]


def delete_group(group: str, password: str) -> None:
    """Delete an entire group."""
    groups = _get_groups(password)
    if group not in groups:
        raise GroupError(f"Group '{group}' does not exist")
    del groups[group]
    _save_groups(groups, password)
