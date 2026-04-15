# Vault Groups Feature

The **group** feature lets you organize vaults into named groups, making it easier to manage related environments (e.g., all production vaults, or all vaults for a specific project).

## Overview

Groups are stored in a special internal meta-vault (`__envault_meta__`) using the same encrypted storage as regular vaults. A single master password is used to access and update group membership.

## Functions

### `add_to_group(vault_name, group, password)`
Adds a vault to the specified group. Creates the group if it doesn't exist. Duplicate entries are ignored.

### `remove_from_group(vault_name, group, password)`
Removes a vault from a group. Raises `GroupError` if the vault is not a member.

### `list_groups(password)`
Returns a dict of all groups and their members.

### `get_group_members(group, password)`
Returns the list of vault names in a group. Raises `GroupError` if the group doesn't exist.

### `delete_group(group, password)`
Deletes an entire group. Raises `GroupError` if the group doesn't exist.

## CLI Commands

| Command | Description |
|---|---|
| `cmd_group_add(vault, group, pw)` | Add vault to group |
| `cmd_group_remove(vault, group, pw)` | Remove vault from group |
| `cmd_group_list(pw)` | List all groups |
| `cmd_group_members(group, pw)` | Show members of a group |
| `cmd_group_delete(group, pw)` | Delete a group |

## Example

```python
from envault.cli_group import cmd_group_add, cmd_group_list

cmd_group_add("prod-us", "production", password="secret")
cmd_group_add("prod-eu", "production", password="secret")

result = cmd_group_list(password="secret")
print(result["groups"])
# {'production': ['prod-us', 'prod-eu']}
```

## Notes

- Group data is encrypted alongside vault data using the same password.
- Deleting a group does not delete the vaults themselves.
- An empty group is preserved until explicitly deleted.
