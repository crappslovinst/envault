# Vault Sharing

The **share** feature lets you export an encrypted vault bundle and hand it off to another developer, who can then import it into their own envault setup with a new password.

## How it works

1. **Export**: The vault's env vars are serialised to JSON, encrypted with a *bundle password* (separate from the vault password), and base64-encoded into a portable string.
2. **Transfer**: Send the bundle string or save it to a file and share it out-of-band (e.g. a secure paste, file transfer).
3. **Import**: The recipient decrypts the bundle with the agreed bundle password and stores the vault locally under a new password of their choice.

## API

### `export_bundle(vault_name, password, bundle_password) -> str`
Returns a base64-encoded encrypted bundle.

### `import_bundle(bundle, bundle_password, new_password, vault_name=None) -> dict`
Decrypts and stores the vault. Returns `{"vault": ..., "keys_imported": ...}`.

### `save_bundle_to_file(bundle, path)` / `load_bundle_from_file(path) -> str`
Helpers for file-based transfer.

## CLI wrappers

```python
from envault.cli_share import cmd_share_export, cmd_share_import

# Export
result = cmd_share_export("myapp", "mypass", "bundlepass", output_file="myapp.bundle")
print(result["bundle"])  # also printed / saved

# Import
result = cmd_share_import("myapp.bundle", "bundlepass", "mynewpass", from_file=True)
print(result)  # {'vault': 'myapp', 'keys_imported': 5}
```

## Security notes

- The bundle password is **independent** of the vault password — choose a strong one.
- Bundles are encrypted with the same AES-based scheme used for vault storage (`envault/crypto.py`).
- All export/import actions are recorded in the audit log.
- Never commit bundle files to version control — add `*.bundle` to `.gitignore`.
