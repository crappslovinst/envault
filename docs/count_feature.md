# Vault Key Count Feature

The `env_count` module provides statistics about the keys stored in a vault.

## What it does

- Counts total, empty, and non-empty keys
- Groups keys by prefix (e.g. `APP_HOST` → prefix `APP`)
- Returns a structured summary dict
- Formats results as a human-readable string

## Usage

### Python API

```python
from envault.env_count import count_keys, format_count_result

result = count_keys("myproject", "mypassword")
print(format_count_result(result))
```

### CLI op

```python
from envault.cli_count import cmd_count

out = cmd_count("myproject", "mypassword")
print(out["formatted"])
```

## Result shape

```json
{
  "vault": "myproject",
  "total": 10,
  "empty": 2,
  "non_empty": 8,
  "prefixes": {
    "APP": 4,
    "DB": 3,
    "SECRET": 3
  }
}
```

## Errors

`CountError` is raised if the vault cannot be loaded (wrong password, missing vault, etc.).
