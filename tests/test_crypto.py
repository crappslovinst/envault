"""Tests for envault.crypto encryption/decryption utilities."""

import pytest
from envault.crypto import encrypt, decrypt


PASSWORD = "super-secret-passphrase"
PLAINTEXT = "DB_HOST=localhost\nDB_PORT=5432\nSECRET_KEY=abc123"


def test_encrypt_returns_string():
    result = encrypt(PLAINTEXT, PASSWORD)
    assert isinstance(result, str)
    assert len(result) > 0


def test_encrypt_is_non_deterministic():
    """Each encryption call should produce a different ciphertext due to random salt/nonce."""
    enc1 = encrypt(PLAINTEXT, PASSWORD)
    enc2 = encrypt(PLAINTEXT, PASSWORD)
    assert enc1 != enc2


def test_decrypt_roundtrip():
    encrypted = encrypt(PLAINTEXT, PASSWORD)
    decrypted = decrypt(encrypted, PASSWORD)
    assert decrypted == PLAINTEXT


def test_decrypt_wrong_password_raises():
    encrypted = encrypt(PLAINTEXT, PASSWORD)
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt(encrypted, "wrong-password")


def test_decrypt_invalid_data_raises():
    with pytest.raises(ValueError):
        decrypt("not-valid-base64!!!", PASSWORD)


def test_encrypt_empty_string():
    encrypted = encrypt("", PASSWORD)
    assert decrypt(encrypted, PASSWORD) == ""


def test_encrypt_unicode():
    text = "API_KEY=こんにちは🔑"
    encrypted = encrypt(text, PASSWORD)
    assert decrypt(encrypted, PASSWORD) == text
