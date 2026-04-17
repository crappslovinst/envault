# Vault Stats Feature

The `env_stats` module provides statistical analysis of a vault's environment variables.

## Functions

### `get_stats(vault_name, password) -> dict`

Returns a dictionary with the following fields:

| Field             | Description                              |
|-------------------|------------------------------------------|
| `total`           | Total number of keys                     |
| `empty`           | Keys with empty string values            |
| `non_empty`       | Keys with non-empty values               |
| `avg_key_length`  | Average character length of all keys     |
| `avg_value_length`| Average character length of non-empty values |
| `longest_key`     | The key with the most characters         |
| `shortest_key`    | The key with the fewest characters       |
| `prefixes`        | Count of keys grouped by `PREFIX_` part  |

### `format_stats(stats) -> str`

Formats the stats dict into a human-readable string.

## CLI

### `cmd_stats(vault_name, password, raw=False) -> dict`

Returns `{ ok, stats, formatted? }`. Pass `raw=True` to omit the formatted string.

## Example

```python
from envault.cli_stats import cmd_stats

result = cmd_stats("production", "mypassword")
print(result["formatted"])
```

## Errors

- `StatsError` is raised (and caught by the CLI layer) if the vault cannot be loaded.
