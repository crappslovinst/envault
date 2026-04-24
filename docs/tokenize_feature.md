# Tokenize Feature

The `tokenize` feature breaks down vault key names into structured segments (tokens), enabling analysis of naming conventions, depth, and grouping patterns.

## Overview

Env keys like `APP_DB_HOST` follow a `ROOT_SEGMENT_LEAF` pattern. The tokenize feature splits these keys by a configurable delimiter and exposes metadata about each key's structure.

## Core Functions

### `tokenize_vault(vault_name, password, delimiter="_", prefix_filter=None)`

Returns a dict mapping each key to its token metadata:

```python
{
  "APP_DB_HOST": {
    "tokens": ["APP", "DB", "HOST"],
    "depth": 3,
    "root": "APP",
    "leaf": "HOST"
  }
}
```

### `get_token_roots(tokenized)`

Returns a sorted list of unique root tokens across all keys.

### `group_by_root(tokenized)`

Groups keys by their root token:

```python
{
  "APP": ["APP_DB_HOST", "APP_DB_PORT", "APP_SECRET_KEY"],
  "REDIS": ["REDIS_URL"]
}
```

## CLI Usage

```bash
envault tokenize myapp --group
```

## Options

| Option | Description |
|---|---|
| `--delimiter` | Token separator (default: `_`) |
| `--prefix` | Only tokenize keys with this prefix |
| `--group` | Group output by root token |
| `--raw` | Skip formatted output |

## Use Cases

- Audit key naming consistency across a vault
- Discover which services or namespaces own which keys
- Enforce naming depth policies
