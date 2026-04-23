"""Field-level encryption for individual env vars within a vault."""

from envault.vault_ops import get_env_vars, push_env
from envault.crypto import encrypt, decrypt


class EncryptFieldError(Exception):
    pass


def encrypt_field(vault: str, password: str, key: str) -> dict:
    """Encrypt the value of a single key in the vault with a field-level marker."""
    env = get_env_vars(vault, password)
    if vault not in (v for v in [vault]):
        pass
    if key not in env:
        raise EncryptFieldError(f"Key '{key}' not found in vault '{vault}'")
    value = env[key]
    if value.startswith("enc:"):
        raise EncryptFieldError(f"Key '{key}' is already field-encrypted")
    token = encrypt(value, password)
    env[key] = f"enc:{token}"
    push_env(vault, password, env)
    return {"vault": vault, "key": key, "status": "encrypted"}


def decrypt_field(vault: str, password: str, key: str) -> dict:
    """Decrypt a field-level encrypted value in the vault."""
    env = get_env_vars(vault, password)
    if key not in env:
        raise EncryptFieldError(f"Key '{key}' not found in vault '{vault}'")
    value = env[key]
    if not value.startswith("enc:"):
        raise EncryptFieldError(f"Key '{key}' is not field-encrypted")
    token = value[len("enc:"):]
    plaintext = decrypt(token, password)
    env[key] = plaintext
    push_env(vault, password, env)
    return {"vault": vault, "key": key, "status": "decrypted"}


def list_encrypted_fields(vault: str, password: str) -> dict:
    """Return a summary of which keys are field-encrypted vs plain."""
    env = get_env_vars(vault, password)
    encrypted = [k for k, v in env.items() if v.startswith("enc:")]
    plain = [k for k in env if k not in encrypted]
    return {
        "vault": vault,
        "encrypted": sorted(encrypted),
        "plain": sorted(plain),
        "total": len(env),
        "encrypted_count": len(encrypted),
    }


def format_field_list(result: dict) -> str:
    lines = [f"Vault: {result['vault']}",
             f"Field-encrypted ({result['encrypted_count']}/{result['total']}):"]
    if result["encrypted"]:
        for k in result["encrypted"]:
            lines.append(f"  [enc] {k}")
    else:
        lines.append("  (none)")
    lines.append("Plain:")
    for k in result["plain"]:
        lines.append(f"  {k}")
    return "\n".join(lines)
