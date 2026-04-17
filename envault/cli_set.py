from envault.env_set import SetError, set_key, delete_key, set_many


def cmd_set(vault: str, password: str, key: str, value: str, overwrite: bool = True) -> dict:
    """CLI command to set a key in a vault."""
    try:
        result = set_key(vault, password, key, value, overwrite=overwrite)
        result["ok"] = True
        return result
    except SetError as e:
        return {"ok": False, "error": str(e)}


def cmd_delete(vault: str, password: str, key: str) -> dict:
    """CLI command to delete a key from a vault."""
    try:
        result = delete_key(vault, password, key)
        result["ok"] = True
        return result
    except SetError as e:
        return {"ok": False, "error": str(e)}


def cmd_set_many(vault: str, password: str, pairs: dict, overwrite: bool = True) -> dict:
    """CLI command to set multiple keys at once."""
    try:
        result = set_many(vault, password, pairs, overwrite=overwrite)
        result["ok"] = True
        return result
    except SetError as e:
        return {"ok": False, "error": str(e)}
