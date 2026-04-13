"""Tag management for vaults — attach, remove, and filter vaults by tags."""

from __future__ import annotations

from typing import Dict, List

from envault.storage import load_vault, save_vault, vault_exists

TAGS_KEY = "__tags__"


class TagError(Exception):
    pass


def get_tags(vault_name: str, password: str) -> List[str]:
    """Return the list of tags for a vault."""
    if not vault_exists(vault_name):
        raise TagError(f"Vault '{vault_name}' not found.")
    data = load_vault(vault_name, password)
    return list(data.get(TAGS_KEY, []))


def add_tag(vault_name: str, password: str, tag: str) -> List[str]:
    """Add a tag to a vault. Returns updated tag list."""
    if not vault_exists(vault_name):
        raise TagError(f"Vault '{vault_name}' not found.")
    tag = tag.strip().lower()
    if not tag:
        raise TagError("Tag must not be empty.")
    data = load_vault(vault_name, password)
    tags: List[str] = list(data.get(TAGS_KEY, []))
    if tag not in tags:
        tags.append(tag)
        data[TAGS_KEY] = tags
        save_vault(vault_name, data, password)
    return tags


def remove_tag(vault_name: str, password: str, tag: str) -> List[str]:
    """Remove a tag from a vault. Returns updated tag list."""
    if not vault_exists(vault_name):
        raise TagError(f"Vault '{vault_name}' not found.")
    tag = tag.strip().lower()
    data = load_vault(vault_name, password)
    tags: List[str] = list(data.get(TAGS_KEY, []))
    if tag not in tags:
        raise TagError(f"Tag '{tag}' not found on vault '{vault_name}'.")
    tags.remove(tag)
    data[TAGS_KEY] = tags
    save_vault(vault_name, data, password)
    return tags


def filter_vaults_by_tag(vault_names: List[str], password: str, tag: str) -> List[str]:
    """Return only those vaults that carry the given tag."""
    tag = tag.strip().lower()
    matched = []
    for name in vault_names:
        try:
            if tag in get_tags(name, password):
                matched.append(name)
        except Exception:
            continue
    return matched
