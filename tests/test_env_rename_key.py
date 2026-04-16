import pytest
from unittest.mock import patch, MagicMock
from envault.env_rename_key import rename_key, RenameKeyError


SAMPLE_ENV = {"OLD_KEY": "secret", "OTHER": "value"}


@pytest.fixture
def mock_rename_deps():
    with patch("envault.env_rename_key.get_env_vars") as _get, \
         patch("envault.env_rename_key.push_env") as _push, \
         patch("envault.env_rename_key.record_event") as _audit:
        _get.return_value = dict(SAMPLE_ENV)
        yield _get, _push, _audit


def test_rename_key_returns_summary(mock_rename_deps):
    _get, _push, _audit = mock_rename_deps
    result = rename_key("myvault", "pass", "OLD_KEY", "NEW_KEY")
    assert result["old_key"] == "OLD_KEY"
    assert result["new_key"] == "NEW_KEY"
    assert result["vault"] == "myvault"
    assert result["value_preserved"] is True


def test_rename_key_pushes_updated_env(mock_rename_deps):
    _get, _push, _audit = mock_rename_deps
    rename_key("myvault", "pass", "OLD_KEY", "NEW_KEY")
    pushed_env = _push.call_args[0][2]
    assert "NEW_KEY" in pushed_env
    assert "OLD_KEY" not in pushed_env
    assert pushed_env["NEW_KEY"] == "secret"


def test_rename_key_preserves_other_keys(mock_rename_deps):
    _get, _push, _audit = mock_rename_deps
    rename_key("myvault", "pass", "OLD_KEY", "NEW_KEY")
    pushed_env = _push.call_args[0][2]
    assert pushed_env["OTHER"] == "value"


def test_rename_key_raises_if_old_key_missing(mock_rename_deps):
    _get, _push, _audit = mock_rename_deps
    with pytest.raises(RenameKeyError, match="not found"):
        rename_key("myvault", "pass", "MISSING_KEY", "NEW_KEY")


def test_rename_key_raises_if_new_key_exists_no_overwrite(mock_rename_deps):
    _get, _push, _audit = mock_rename_deps
    with pytest.raises(RenameKeyError, match="already exists"):
        rename_key("myvault", "pass", "OLD_KEY", "OTHER")


def test_rename_key_allows_overwrite(mock_rename_deps):
    _get, _push, _audit = mock_rename_deps
    result = rename_key("myvault", "pass", "OLD_KEY", "OTHER", overwrite=True)
    assert result["overwrite"] is True
    pushed_env = _push.call_args[0][2]
    assert pushed_env["OTHER"] == "secret"


def test_rename_key_records_audit_event(mock_rename_deps):
    _get, _push, _audit = mock_rename_deps
    rename_key("myvault", "pass", "OLD_KEY", "NEW_KEY")
    _audit.assert_called_once_with("myvault", "rename_key", {"old_key": "OLD_KEY", "new_key": "NEW_KEY"})


def test_rename_key_raises_if_vault_missing(mock_rename_deps):
    _get, _push, _audit = mock_rename_deps
    _get.side_effect = Exception("vault not found")
    with pytest.raises(RenameKeyError, match="Could not load vault"):
        rename_key("ghost", "pass", "K", "K2")
