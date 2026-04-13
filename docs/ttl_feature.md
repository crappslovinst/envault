# TTL (Time-to-Live) for Vaults

Envault supports attaching an expiry window to any vault. Once the TTL elapses the vault is considered **expired** and tooling can gate access accordingly.

## Concepts

| Term | Meaning |
|------|---------|
| TTL | Duration in seconds before a vault expires |
| `expires_at` | Unix timestamp when the vault expires |
| Expired | `expires_at` is in the past |

TTL metadata is stored inside the encrypted vault payload under reserved keys (`__envault_ttl__`, `__envault_expires_at__`), so it is protected by the same password as the rest of the data.

## API

### `set_ttl(vault_name, password, seconds) -> dict`
Attach a TTL to a vault. Overwrites any existing TTL.

```python
from envault.ttl import set_ttl
set_ttl("production", "s3cr3t", 86400)  # expires in 24 h
```

### `get_ttl(vault_name, password) -> dict | None`
Return TTL info, or `None` if no TTL is set.

```python
info = get_ttl("production", "s3cr3t")
# {'vault': 'production', 'ttl_seconds': 86400, 'expires_at': ...,
#  'remaining_seconds': 72000.0, 'expired': False}
```

### `clear_ttl(vault_name, password) -> dict`
Remove TTL metadata from a vault.

### `is_expired(vault_name, password) -> bool`
Quick boolean check — returns `True` only when a TTL exists **and** has passed.

## CLI helpers (`cli_ttl.py`)

| Function | Purpose |
|----------|---------|
| `cmd_set_ttl` | Set TTL, returns status dict |
| `cmd_get_ttl` | Show TTL info |
| `cmd_clear_ttl` | Remove TTL |
| `cmd_check_expired` | Boolean expiry check |
| `format_ttl_info` | Human-readable one-liner |

## Notes

- Envault does **not** automatically delete expired vaults. Expiry is advisory — callers decide what to do (warn, block, purge).
- TTL keys are stripped from the visible env-var surface by `get_env_vars` since they start with `__envault_`.
