"""Type casting utilities for vault env vars."""

from envault.vault_ops import get_env_vars


class TypecastError(Exception):
    pass


_TRUTHY = {"true", "1", "yes", "on"}
_FALSY = {"false", "0", "no", "off"}


def _cast_value(value: str, target_type: str):
    """Attempt to cast a string value to the given type name."""
    t = target_type.lower()
    if t == "int":
        try:
            return int(value)
        except ValueError:
            raise TypecastError(f"Cannot cast {value!r} to int")
    if t == "float":
        try:
            return float(value)
        except ValueError:
            raise TypecastError(f"Cannot cast {value!r} to float")
    if t == "bool":
        v = value.strip().lower()
        if v in _TRUTHY:
            return True
        if v in _FALSY:
            return False
        raise TypecastError(f"Cannot cast {value!r} to bool")
    if t == "str":
        return value
    raise TypecastError(f"Unknown target type: {target_type!r}")


def typecast_vault(vault_name: str, password: str, schema: dict) -> dict:
    """Cast env vars according to a type schema.

    schema: {KEY: 'int' | 'float' | 'bool' | 'str'}
    Returns a dict with cast values and a report of errors.
    """
    try:
        env = get_env_vars(vault_name, password)
    except Exception as exc:
        raise TypecastError(str(exc)) from exc

    results = {}
    errors = {}
    for key, target_type in schema.items():
        if key not in env:
            errors[key] = "key not found"
            continue
        try:
            results[key] = _cast_value(env[key], target_type)
        except TypecastError as exc:
            errors[key] = str(exc)

    return {
        "vault": vault_name,
        "cast": results,
        "errors": errors,
        "total": len(schema),
        "success": len(results),
        "failed": len(errors),
    }


def format_typecast_result(result: dict) -> str:
    lines = [
        f"Vault : {result['vault']}",
        f"Total : {result['total']}",
        f"OK    : {result['success']}",
        f"Failed: {result['failed']}",
    ]
    if result["cast"]:
        lines.append("\nCast values:")
        for k, v in sorted(result["cast"].items()):
            lines.append(f"  {k} = {v!r} ({type(v).__name__})")
    if result["errors"]:
        lines.append("\nErrors:")
        for k, msg in sorted(result["errors"].items()):
            lines.append(f"  {k}: {msg}")
    return "\n".join(lines)
