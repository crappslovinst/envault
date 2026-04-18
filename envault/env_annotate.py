"""Annotation support: attach human-readable comments to individual keys in a vault."""

from envault.storage import load_vault, save_vault, vault_exists


class AnnotateError(Exception):
    pass


def _get_annotations(vault_name: str, password: str) -> dict:
    data = load_vault(vault_name, password)
    return data.get("__annotations__", {})


def set_annotation(vault_name: str, password: str, key: str, note: str) -> dict:
    if not vault_exists(vault_name):
        raise AnnotateError(f"Vault '{vault_name}' not found.")
    data = load_vault(vault_name, password)
    annotations = data.get("__annotations__", {})
    annotations[key] = note
    data["__annotations__"] = annotations
    save_vault(vault_name, password, data)
    return {"vault": vault_name, "key": key, "annotation": note, "status": "set"}


def remove_annotation(vault_name: str, password: str, key: str) -> dict:
    if not vault_exists(vault_name):
        raise AnnotateError(f"Vault '{vault_name}' not found.")
    data = load_vault(vault_name, password)
    annotations = data.get("__annotations__", {})
    if key not in annotations:
        raise AnnotateError(f"No annotation found for key '{key}'.")
    del annotations[key]
    data["__annotations__"] = annotations
    save_vault(vault_name, password, data)
    return {"vault": vault_name, "key": key, "status": "removed"}


def get_annotations(vault_name: str, password: str, key: str = None) -> dict:
    if not vault_exists(vault_name):
        raise AnnotateError(f"Vault '{vault_name}' not found.")
    annotations = _get_annotations(vault_name, password)
    if key:
        return {key: annotations.get(key)}
    return dict(annotations)


def format_annotations(annotations: dict) -> str:
    if not annotations:
        return "No annotations."
    lines = [f"  {k}: {v}" for k, v in sorted(annotations.items())]
    return "Annotations:\n" + "\n".join(lines)
