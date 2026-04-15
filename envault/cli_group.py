"""CLI operations for vault group management."""

from envault.env_group import (
    GroupError,
    add_to_group,
    remove_from_group,
    list_groups,
    get_group_members,
    delete_group,
)


def cmd_group_add(vault_name: str, group: str, password: str) -> dict:
    """Add a vault to a group."""
    try:
        members = add_to_group(vault_name, group, password)
        return {"ok": True, "group": group, "vault": vault_name, "members": members}
    except GroupError as e:
        return {"ok": False, "error": str(e)}


def cmd_group_remove(vault_name: str, group: str, password: str) -> dict:
    """Remove a vault from a group."""
    try:
        members = remove_from_group(vault_name, group, password)
        return {"ok": True, "group": group, "vault": vault_name, "members": members}
    except GroupError as e:
        return {"ok": False, "error": str(e)}


def cmd_group_list(password: str) -> dict:
    """List all groups."""
    groups = list_groups(password)
    return {"ok": True, "groups": groups, "total": len(groups)}


def cmd_group_members(group: str, password: str) -> dict:
    """List members of a group."""
    try:
        members = get_group_members(group, password)
        return {"ok": True, "group": group, "members": members, "count": len(members)}
    except GroupError as e:
        return {"ok": False, "error": str(e)}


def cmd_group_delete(group: str, password: str) -> dict:
    """Delete a group entirely."""
    try:
        delete_group(group, password)
        return {"ok": True, "group": group, "deleted": True}
    except GroupError as e:
        return {"ok": False, "error": str(e)}


def format_group_list(groups: dict) -> str:
    """Format groups dict for display."""
    if not groups:
        return "No groups defined."
    lines = []
    for group, members in sorted(groups.items()):
        member_str = ", ".join(members) if members else "(empty)"
        lines.append(f"  [{group}] {member_str}")
    return "\n".join(lines)
