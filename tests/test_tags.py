"""Tests for envault/tags.py"""

import pytest

from envault.tags import (
    TagError,
    add_tag,
    filter_vaults_by_tag,
    get_tags,
    remove_tag,
)


@pytest.fixture
def patch_vault_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("envault.storage.VAULT_DIR", str(tmp_path))
    monkeypatch.setattr("envault.tags.vault_exists", lambda name: True)
    return tmp_path


@pytest.fixture
def seeded_vault(patch_vault_dir):
    """Push a minimal vault so storage calls work."""
    from envault.storage import save_vault
    save_vault("myapp", {"KEY": "val"}, "secret")
    return "myapp"


def test_get_tags_empty_by_default(seeded_vault):
    assert get_tags("myapp", "secret") == []


def test_add_tag_returns_list(seeded_vault):
    result = add_tag("myapp", "secret", "production")
    assert "production" in result


def test_add_tag_persists(seeded_vault):
    add_tag("myapp", "secret", "staging")
    assert "staging" in get_tags("myapp", "secret")


def test_add_tag_is_lowercased(seeded_vault):
    add_tag("myapp", "secret", "  PROD  ")
    assert "prod" in get_tags("myapp", "secret")


def test_add_tag_no_duplicates(seeded_vault):
    add_tag("myapp", "secret", "ci")
    add_tag("myapp", "secret", "ci")
    assert get_tags("myapp", "secret").count("ci") == 1


def test_add_tag_empty_raises(seeded_vault):
    with pytest.raises(TagError, match="empty"):
        add_tag("myapp", "secret", "   ")


def test_remove_tag(seeded_vault):
    add_tag("myapp", "secret", "beta")
    remaining = remove_tag("myapp", "secret", "beta")
    assert "beta" not in remaining


def test_remove_tag_not_present_raises(seeded_vault):
    with pytest.raises(TagError, match="not found"):
        remove_tag("myapp", "secret", "nonexistent")


def test_get_tags_vault_missing(patch_vault_dir, monkeypatch):
    monkeypatch.setattr("envault.tags.vault_exists", lambda name: False)
    with pytest.raises(TagError, match="not found"):
        get_tags("ghost", "secret")


def test_filter_vaults_by_tag(patch_vault_dir):
    from envault.storage import save_vault
    save_vault("app1", {"__tags__": ["prod"], "K": "v"}, "pw")
    save_vault("app2", {"__tags__": ["dev"], "K": "v"}, "pw")
    save_vault("app3", {"__tags__": ["prod", "eu"], "K": "v"}, "pw")

    result = filter_vaults_by_tag(["app1", "app2", "app3"], "pw", "prod")
    assert "app1" in result
    assert "app3" in result
    assert "app2" not in result


def test_filter_vaults_skips_errors(patch_vault_dir, monkeypatch):
    """Vaults that raise during load are silently skipped."""
    from envault.storage import save_vault
    save_vault("ok", {"__tags__": ["x"], "K": "v"}, "pw")

    result = filter_vaults_by_tag(["ok", "bad_vault"], "pw", "x")
    assert result == ["ok"]
