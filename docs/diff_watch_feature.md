# Diff Watch Feature

The **diff watch** feature lets you monitor a local `.env` file in real time and
see how it diverges from a saved vault — useful during active development when
you're tweaking local config and want to stay in sync.

## Functions

### `snapshot_diff(vault_name, password, env_file) -> list`

Returns a one-shot diff between the current vault contents and a local `.env`
file. Each entry in the list has `key`, `status` (`added`, `removed`,
`changed`, `unchanged`), and optionally `old` / `new` values.

```python
from envault.env_diff_watch import snapshot_diff
from envault.diff import format_diff

result = snapshot_diff("myapp", "s3cr3t", ".env")
print(format_diff(result))
```

### `watch_diff(vault_name, password, env_file, interval, max_iterations, on_diff)`

Polls the file every `interval` seconds. When the file hash changes, it parses
the new content and emits a diff via the optional `on_diff` callback. Each
change is also recorded in the audit log.

```python
from envault.env_diff_watch import watch_diff
from envault.diff import format_diff

watch_diff("myapp", "s3cr3t", ".env", on_diff=lambda d: print(format_diff(d)))
```

## CLI helpers

| Function | Description |
|---|---|
| `cmd_snapshot_diff` | One-shot diff, returns structured result |
| `cmd_watch_diff` | Blocking watch loop, prints diffs as they occur |

## Errors

- `DiffWatchError` — raised when the file or vault cannot be loaded.
