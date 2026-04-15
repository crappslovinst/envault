"""CLI operations for schema validation."""

import json
from envault.env_schema import validate_schema, SchemaError


def cmd_validate_schema(vault_name: str, password: str, schema_path: str) -> dict:
    """
    Load a JSON schema file and validate the vault against it.
    Returns a result dict with status, errors, and warnings.
    """
    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)
    except FileNotFoundError:
        return {"status": "error", "message": f"Schema file not found: {schema_path}"}
    except json.JSONDecodeError as exc:
        return {"status": "error", "message": f"Invalid JSON in schema file: {exc}"}

    try:
        result = validate_schema(vault_name, password, schema)
    except SchemaError as exc:
        return {"status": "error", "message": str(exc)}

    status = "ok" if result["passed"] else "failed"
    return {
        "status": status,
        "vault": vault_name,
        "passed": result["passed"],
        "errors": result["errors"],
        "warnings": result["warnings"],
        "error_count": len(result["errors"]),
        "warning_count": len(result["warnings"]),
    }


def format_schema_result(result: dict) -> str:
    """Format a schema validation result for human-readable CLI output."""
    if result["status"] == "error":
        return f"[error] {result['message']}"

    lines = []
    vault = result.get("vault", "?")
    if result["passed"]:
        lines.append(f"[ok] vault '{vault}' passed schema validation")
    else:
        lines.append(f"[failed] vault '{vault}' failed schema validation")

    for err in result.get("errors", []):
        lines.append(f"  [error] {err['key']}: {err['issue']}")

    for warn in result.get("warnings", []):
        lines.append(f"  [warn]  {warn['key']}: {warn['issue']}")

    ec = result.get("error_count", 0)
    wc = result.get("warning_count", 0)
    lines.append(f"  {ec} error(s), {wc} warning(s)")
    return "\n".join(lines)
