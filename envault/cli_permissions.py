"""CLI commands for vault permission management."""

from envault.env_permissions import (
    PermissionError,
    set_permission,
    remove_permission,
    get_permission,
    list_permissions,
    check_permission,
)


def cmd_set_permission(vault: str, password: str, user: str, role: str) -> dict:
    try:
        result = set_permission(vault, password, user, role)
        return {"ok": True, **result}
    except PermissionError as e:
        return {"ok": False, "error": str(e)}


def cmd_remove_permission(vault: str, password: str, user: str) -> dict:
    try:
        result = remove_permission(vault, password, user)
        return {"ok": True, **result}
    except PermissionError as e:
        return {"ok": False, "error": str(e)}


def cmd_get_permission(vault: str, password: str, user: str) -> dict:
    try:
        role = get_permission(vault, password, user)
        if role is None:
            return {"ok": True, "vault": vault, "user": user, "role": None, "message": "No permission set."}
        return {"ok": True, "vault": vault, "user": user, "role": role}
    except PermissionError as e:
        return {"ok": False, "error": str(e)}


def cmd_list_permissions(vault: str, password: str) -> dict:
    try:
        perms = list_permissions(vault, password)
        return {"ok": True, "vault": vault, "permissions": perms}
    except PermissionError as e:
        return {"ok": False, "error": str(e)}


def format_permissions(perms: dict) -> str:
    if not perms:
        return "  (no permissions set)"
    lines = [f"  {user}: {role}" for user, role in sorted(perms.items())]
    return "\n".join(lines)
