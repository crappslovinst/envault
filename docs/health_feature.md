# Vault Health Check

The health check feature lets you quickly assess the overall state of a vault.

## What it checks

| Check | Description |
|---|---|
| **Key count** | Total number of env vars stored in the vault |
| **TTL / expiry** | Whether the vault has passed its TTL deadline |
| **Lint** | Runs the built-in linter (uppercase keys, empty values, placeholders) |
| **Required keys** | Optionally verify that a set of keys are present |

## Python API

```python
from envault.env_health import check_health, format_health_report

report = check_health("production", password="s3cr3t", required_keys=["DATABASE_URL", "SECRET_KEY"])
print(format_health_report(report))
```

### Return shape

```python
{
    "vault": "production",
    "ok": False,
    "issues": ["missing required keys: SECRET_KEY"],
    "ttl": {"expires_at": "2025-06-01T00:00:00"},
    "expired": False,
    "lint": {"issue_count": 0, "issues": []},
    "missing_keys": ["SECRET_KEY"],
    "key_count": 12,
}
```

## CLI wrapper

```python
from envault.cli_health import cmd_health

result = cmd_health("production", password="s3cr3t", required_keys=["DATABASE_URL"])
if not result["ok"]:
    print("Vault is unhealthy:", result["error"] or result["report"]["issues"])
```

## Exit semantics

- `ok: True`  — vault is healthy, no action needed.
- `ok: False` — at least one issue was detected; inspect `issues` for details.
