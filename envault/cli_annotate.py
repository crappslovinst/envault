"""CLI commands for vault key annotations."""

from envault.env_annotate import AnnotateError, set_annotation, remove_annotation, get_annotations, format_annotations


def cmd_set_annotation(vault: str, password: str, key: str, note: str) -> dict:
    try:
        result = set_annotation(vault, password, key, note)
        result["formatted"] = f"Annotation set for '{key}' in vault '{vault}'."
        return result
    except AnnotateError as e:
        return {"error": str(e)}


def cmd_remove_annotation(vault: str, password: str, key: str) -> dict:
    try:
        result = remove_annotation(vault, password, key)
        result["formatted"] = f"Annotation removed for '{key}' in vault '{vault}'."
        return result
    except AnnotateError as e:
        return {"error": str(e)}


def cmd_get_annotations(vault: str, password: str, key: str = None) -> dict:
    try:
        annotations = get_annotations(vault, password, key)
        return {
            "vault": vault,
            "annotations": annotations,
            "formatted": format_annotations(annotations),
        }
    except AnnotateError as e:
        return {"error": str(e)}
