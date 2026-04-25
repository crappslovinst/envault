# Normalize Feature

The `normalize` command cleans up vault values by:

- **Trimming whitespace** from the start and end of every value.
- **Standardising boolean strings** — any variant of `true/yes/1/on` becomes `true`
  and any variant of `false/no/0/off` becomes `false` (case-insensitive).

## Usage

```bash
# Normalize and write changes
envault normalize myapp --password secret

# Preview changes without writing
envault normalize myapp --password secret --dry-run

# Skip boolean normalization
envault normalize myapp --password secret --no-bools
```

## Example

Before:
```
DEBUG=True
ACTIVE=YES
NAME=  myapp  
PORT=8080
```

After:
```
DEBUG=true
ACTIVE=true
NAME=myapp
PORT=8080
```

## Python API

```python
from envault.env_normalize import normalize_vault

result = normalize_vault("myapp", password="secret", dry_run=False)
print(result["changed"])       # number of changed keys
print(result["changed_keys"])  # list of key names that changed
```

## Return value

| Field          | Type      | Description                              |
|----------------|-----------|------------------------------------------|
| `vault`        | `str`     | Vault name                               |
| `total`        | `int`     | Total number of keys                     |
| `changed`      | `int`     | Number of keys whose value was altered   |
| `changed_keys` | `list`    | Names of altered keys                    |
| `dry_run`      | `bool`    | Whether changes were actually persisted  |
