"""Tests for envault/share.py"""

import pytest
from unittest.mock import patch, MagicMock

from envault.share import (
    export_bundle,
    import_bundle,
    save_bundle_to_file,
    load_bundle_from_file,
    ShareError,
)


ENV_VARS = {"DB_HOST": "localhost", "SECRET": "abc123"}


@pytest.fixture()
 def mock_share_deps(tmp_path):
    with patch("envault.share.get_env_vars", return_value=ENV_VARS) as mock_get, \
         patch("envault.share.push_env") as mock_push, \
         patch("envault.share.record_event") as mock_audit:
        yield {"get": mock_get, "push": mock_push, "audit": mock_audit}


def test_export_bundle_returns_string(mock_share_deps):
    bundle = export_bundle("myapp", "pass", "bundlepass")
    assert isinstance(bundle, str)
    assert len(bundle) > 0


def test_export_bundle_records_audit(mock_share_deps):
    export_bundle("myapp", "pass", "bundlepass")
    mock_share_deps["audit"].assert_called_once()
    args = mock_share_deps["audit"].call_args[0]
    assert args[0] == "myapp"
    assert args[1] == "share_export"


def test_export_bundle_raises_if_vault_missing():
    with patch("envault.share.get_env_vars", return_value=None):
        with pytest.raises(ShareError, match="not found"):
            export_bundle("ghost", "pass", "bundlepass")


def test_import_bundle_roundtrip(mock_share_deps):
    bundle = export_bundle("myapp", "pass", "bundlepass")
    result = import_bundle(bundle, "bundlepass", "newpass", "imported_app")
    assert result["vault"] == "imported_app"
    assert result["keys_imported"] == len(ENV_VARS)


def test_import_bundle_uses_original_vault_name_if_none(mock_share_deps):
    bundle = export_bundle("myapp", "pass", "bundlepass")
    result = import_bundle(bundle, "bundlepass", "newpass")
    assert result["vault"] == "myapp"


def test_import_bundle_wrong_password_raises(mock_share_deps):
    bundle = export_bundle("myapp", "pass", "bundlepass")
    with pytest.raises(ShareError, match="decrypt"):
        import_bundle(bundle, "wrongpass", "newpass")


def test_import_bundle_invalid_format_raises():
    with pytest.raises(ShareError, match="Invalid bundle"):
        import_bundle("not-valid-base64!!!", "anypass", "newpass")


def test_import_bundle_calls_push(mock_share_deps):
    bundle = export_bundle("myapp", "pass", "bundlepass")
    import_bundle(bundle, "bundlepass", "newpass", "dest")
    mock_share_deps["push"].assert_called_once_with("dest", "newpass", ENV_VARS)


def test_save_and_load_bundle_file(tmp_path, mock_share_deps):
    bundle = export_bundle("myapp", "pass", "bundlepass")
    fpath = str(tmp_path / "vault.bundle")
    save_bundle_to_file(bundle, fpath)
    loaded = load_bundle_from_file(fpath)
    assert loaded == bundle


def test_load_bundle_missing_file_raises():
    with pytest.raises(ShareError, match="not found"):
        load_bundle_from_file("/nonexistent/path/bundle.txt")
