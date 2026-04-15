"""Schema validation for vault env vars — type checks, allowed values, regex patterns."""

import re
from envault.vault_ops import get_env_vars


class SchemaError(Exception):
    pass


SUPPORTED_TYPES = {"str", "int", "float", "bool"}


def _check_type(value: str, expected_type: str) -> bool:
    try:
        if expected_type == "int":
            int(value)
        elif expected_type == "float":
            float(value)
        elif expected_type == "bool":
            if value.lower() not in ("true", "false", "1", "0", "yes", "no"):
                return False
        # str always passes
    except (ValueError, TypeError):
        return False
    return True


def validate_schema(vault_name: str, password: str, schema: dict) -> dict:
    """
    Validate env vars in a vault against a schema dict.

    Schema format:
        {
            "KEY": {
                "type": "str" | "int" | "float" | "bool",   # optional
                "pattern": "<regex>",                        # optional
                "allowed": ["val1", "val2"],                 # optional
                "required": True | False                     # optional, default False
            }
        }

    Returns a dict with keys: "errors", "warnings", "passed".
    """
    try:
        env_vars = get_env_vars(vault_name, password)
    except Exception as exc:
        raise SchemaError(f"Could not load vault '{vault_name}': {exc}") from exc

    errors = []
    warnings = []

    for key, rules in schema.items():
        required = rules.get("required", False)
        value = env_vars.get(key)

        if value is None:
            if required:
                errors.append({"key": key, "issue": "missing required key"})
            else:
                warnings.append({"key": key, "issue": "key not present in vault"})
            continue

        expected_type = rules.get("type")
        if expected_type:
            if expected_type not in SUPPORTED_TYPES:
                raise SchemaError(f"Unsupported type '{expected_type}' for key '{key}'")
            if not _check_type(value, expected_type):
                errors.append({"key": key, "issue": f"expected type '{expected_type}', got '{value}'"})

        pattern = rules.get("pattern")
        if pattern and not re.fullmatch(pattern, value):
            errors.append({"key": key, "issue": f"value '{value}' does not match pattern '{pattern}'"})

        allowed = rules.get("allowed")
        if allowed is not None and value not in allowed:
            errors.append({"key": key, "issue": f"value '{value}' not in allowed list {allowed}"})

    passed = len(errors) == 0
    return {"errors": errors, "warnings": warnings, "passed": passed}
