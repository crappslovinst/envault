"""Per-vault permission management: read, write, admin roles."""

from envault.storage import load_vault, save_vault, vault_exists


class PermissionError(Exception):
    pass


VALID_ROLES = {"read", "write", "admin"}


def _get_permissions(vault_name: str, password: str) -> dict:
    data = load_vault(vault_name, password)
    return data.get("__permissions__", {})


def set_permission(vault_name: str, password: str, user: str, role: str) -> dict:
    """Assign a role to a user for the given vault."""
    if not vault_exists(vault_name):
        raise PermissionError(f"Vault '{vault_name}' not found.")
    if role not in VALID_ROLES:
        raise PermissionError(f"Invalid role '{role}'. Must be one of {VALID_ROLES}.")
    data = load_vault(vault_name, password)
    perms = data.get("__permissions__", {})
    perms[user] = role
    data["__permissions__"] = perms
    save_vault(vault_name, data, password)
    return {"vault": vault_name, "user": user, "role": role}


def remove_permission(vault_name: str, password: str, user: str) -> dict:
    """Remove a user's permission from the vault."""
    if not vault_exists(vault_name):
        raise PermissionError(f"Vault '{vault_name}' not found.")
    data = load_vault(vault_name, password)
    perms = data.get("__permissions__", {})
    if user not in perms:
        raise PermissionError(f"User '{user}' has no permissions on vault '{vault_name}'.")
    del perms[user]
    data["__permissions__"] = perms
    save_vault(vault_name, data, password)
    return {"vault": vault_name, "user": user, "removed": True}


def get_permission(vault_name: str, password: str, user: str) -> str | None:
    """Return the role of a user, or None if not set."""
    if not vault_exists(vault_name):
        raise PermissionError(f"Vault '{vault_name}' not found.")
    perms = _get_permissions(vault_name, password)
    return perms.get(user)


def list_permissions(vault_name: str, password: str) -> dict:
    """Return all user->role mappings for the vault."""
    if not vault_exists(vault_name):
        raise PermissionError(f"Vault '{vault_name}' not found.")
    return _get_permissions(vault_name, password)


def check_permission(vault_name: str, password: str, user: str, required_role: str) -> bool:
    """Return True if user has at least the required_role level."""
    role_rank = {"read": 0, "write": 1, "admin": 2}
    if required_role not in role_rank:
        raise PermissionError(f"Unknown required role: '{required_role}'.")
    perms = _get_permissions(vault_name, password)
    user_role = perms.get(user)
    if user_role is None:
        return False
    return role_rank.get(user_role, -1) >= role_rank[required_role]
