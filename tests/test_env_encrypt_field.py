"""Tests for field-level encryption module."""

import pytest
from unittest.mock import patch, MagicMock

from envault.env_encrypt_field import (
    encrypt_field,
    decrypt_field,
    list_encrypted_fields,
    format_field_list,
    EncryptFieldError,
)


VAULT = "myapp"
PASS = "secret"


@pytest.fixture
def mock_deps():
    with patch("envault.env_encrypt_field.get_env_vars") as _get, \
         patch("envault.env_encrypt_field.push_env") as _push, \
         patch("envault.env_encrypt_field.encrypt") as _enc, \
         patch("envault.env_encrypt_field.decrypt") as _dec:
        yield {"get": _get, "push": _push, "enc": _enc, "dec": _dec}


def test_encrypt_field_returns_summary(mock_deps):
    mock_deps["get"].return_value = {"DB_PASS": "hunter2", "HOST": "localhost"}
    mock_deps["enc"].return_value = "TOKEN123"
    result = encrypt_field(VAULT, PASS, "DB_PASS")
    assert result["vault"] == VAULT
    assert result["key"] == "DB_PASS"
    assert result["status"] == "encrypted"


def test_encrypt_field_writes_enc_prefix(mock_deps):
    mock_deps["get"].return_value = {"DB_PASS": "hunter2"}
    mock_deps["enc"].return_value = "TOKEN123"
    encrypt_field(VAULT, PASS, "DB_PASS")
    pushed_env = mock_deps["push"].call_args[0][2]
    assert pushed_env["DB_PASS"] == "enc:TOKEN123"


def test_encrypt_field_raises_if_key_missing(mock_deps):
    mock_deps["get"].return_value = {"HOST": "localhost"}
    with pytest.raises(EncryptFieldError, match="not found"):
        encrypt_field(VAULT, PASS, "DB_PASS")


def test_encrypt_field_raises_if_already_encrypted(mock_deps):
    mock_deps["get"].return_value = {"DB_PASS": "enc:SOMETOKEN"}
    with pytest.raises(EncryptFieldError, match="already field-encrypted"):
        encrypt_field(VAULT, PASS, "DB_PASS")


def test_decrypt_field_returns_summary(mock_deps):
    mock_deps["get"].return_value = {"DB_PASS": "enc:TOKEN123"}
    mock_deps["dec"].return_value = "hunter2"
    result = decrypt_field(VAULT, PASS, "DB_PASS")
    assert result["status"] == "decrypted"
    assert result["key"] == "DB_PASS"


def test_decrypt_field_restores_plaintext(mock_deps):
    mock_deps["get"].return_value = {"DB_PASS": "enc:TOKEN123"}
    mock_deps["dec"].return_value = "hunter2"
    decrypt_field(VAULT, PASS, "DB_PASS")
    pushed_env = mock_deps["push"].call_args[0][2]
    assert pushed_env["DB_PASS"] == "hunter2"


def test_decrypt_field_raises_if_not_encrypted(mock_deps):
    mock_deps["get"].return_value = {"DB_PASS": "hunter2"}
    with pytest.raises(EncryptFieldError, match="not field-encrypted"):
        decrypt_field(VAULT, PASS, "DB_PASS")


def test_decrypt_field_raises_if_key_missing(mock_deps):
    mock_deps["get"].return_value = {}
    with pytest.raises(EncryptFieldError, match="not found"):
        decrypt_field(VAULT, PASS, "DB_PASS")


def test_list_encrypted_fields_counts(mock_deps):
    mock_deps["get"].return_value = {
        "DB_PASS": "enc:TOKEN",
        "HOST": "localhost",
        "API_KEY": "enc:KEY2",
    }
    result = list_encrypted_fields(VAULT, PASS)
    assert result["encrypted_count"] == 2
    assert result["total"] == 3
    assert "DB_PASS" in result["encrypted"]
    assert "HOST" in result["plain"]


def test_format_field_list_contains_vault_name(mock_deps):
    mock_deps["get"].return_value = {"DB_PASS": "enc:TOKEN", "HOST": "localhost"}
    result = list_encrypted_fields(VAULT, PASS)
    formatted = format_field_list(result)
    assert VAULT in formatted
    assert "[enc]" in formatted
    assert "HOST" in formatted
