"""Tests for envault.storage vault persistence layer."""

import pytest
from pathlib import Path
from envault.storage import save_vault, load_vault, vault_exists, list_vaults, delete_vault


PASSWORD = "test-password-123"
SAMPLE_DATA = {"DB_URL": "postgres://localhost/dev", "DEBUG": "true"}


@pytest.fixture
def tmp_vault_dir(tmp_path):
    return tmp_path / "vaults"


def test_save_and_load_vault(tmp_vault_dir):
    save_vault("myproject", SAMPLE_DATA, PASSWORD, vault_dir=tmp_vault_dir)
    loaded = load_vault("myproject", PASSWORD, vault_dir=tmp_vault_dir)
    assert loaded == SAMPLE_DATA


def test_vault_exists_after_save(tmp_vault_dir):
    assert not vault_exists("myproject", vault_dir=tmp_vault_dir)
    save_vault("myproject", SAMPLE_DATA, PASSWORD, vault_dir=tmp_vault_dir)
    assert vault_exists("myproject", vault_dir=tmp_vault_dir)


def test_list_vaults(tmp_vault_dir):
    save_vault("alpha", SAMPLE_DATA, PASSWORD, vault_dir=tmp_vault_dir)
    save_vault("beta", SAMPLE_DATA, PASSWORD, vault_dir=tmp_vault_dir)
    vaults = list_vaults(vault_dir=tmp_vault_dir)
    assert set(vaults) == {"alpha", "beta"}


def test_list_vaults_empty_dir(tmp_vault_dir):
    assert list_vaults(vault_dir=tmp_vault_dir) == []


def test_load_nonexistent_vault_raises(tmp_vault_dir):
    with pytest.raises(FileNotFoundError):
        load_vault("ghost", PASSWORD, vault_dir=tmp_vault_dir)


def test_load_wrong_password_raises(tmp_vault_dir):
    save_vault("secure", SAMPLE_DATA, PASSWORD, vault_dir=tmp_vault_dir)
    with pytest.raises(ValueError):
        load_vault("secure", "wrong-pass", vault_dir=tmp_vault_dir)


def test_delete_vault(tmp_vault_dir):
    save_vault("todelete", SAMPLE_DATA, PASSWORD, vault_dir=tmp_vault_dir)
    delete_vault("todelete", vault_dir=tmp_vault_dir)
    assert not vault_exists("todelete", vault_dir=tmp_vault_dir)


def test_delete_nonexistent_vault_raises(tmp_vault_dir):
    with pytest.raises(FileNotFoundError):
        delete_vault("nope", vault_dir=tmp_vault_dir)
