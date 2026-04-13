"""Tests for envault/cli_share.py"""

import pytest
from unittest.mock import patch, MagicMock

from envault.cli_share import cmd_share_export, cmd_share_import
from envault.share import ShareError


FAKE_BUNDLE = "ZmFrZWJ1bmRsZWRhdGE="  # base64 of 'fakebundledata'


@pytest.fixture()
def mock_share_fns():
    with patch("envault.cli_share.export_bundle", return_value=FAKE_BUNDLE) as mock_exp, \
         patch("envault.cli_share.import_bundle", return_value={"vault": "v", "keys_imported": 3}) as mock_imp, \
         patch("envault.cli_share.save_bundle_to_file") as mock_save, \
         patch("envault.cli_share.load_bundle_from_file", return_value=FAKE_BUNDLE) as mock_load:
        yield {
            "export": mock_exp,
            "import": mock_imp,
            "save": mock_save,
            "load": mock_load,
        }


def test_cmd_share_export_returns_bundle(mock_share_fns):
    result = cmd_share_export("myapp", "pass", "bpass")
    assert result["bundle"] == FAKE_BUNDLE
    assert result["vault"] == "myapp"
    assert result["saved_to"] is None


def test_cmd_share_export_saves_to_file(mock_share_fns, tmp_path):
    fpath = str(tmp_path / "out.bundle")
    result = cmd_share_export("myapp", "pass", "bpass", output_file=fpath)
    assert result["saved_to"] == fpath
    mock_share_fns["save"].assert_called_once_with(FAKE_BUNDLE, fpath)


def test_cmd_share_import_from_string(mock_share_fns):
    result = cmd_share_import(FAKE_BUNDLE, "bpass", "newpass", vault_name="dest")
    assert result["vault"] == "v"
    mock_share_fns["import"].assert_called_once_with(FAKE_BUNDLE, "bpass", "newpass", "dest")


def test_cmd_share_import_from_file(mock_share_fns):
    result = cmd_share_import("somefile.bundle", "bpass", "newpass", from_file=True)
    mock_share_fns["load"].assert_called_once_with("somefile.bundle")
    mock_share_fns["import"].assert_called_once_with(FAKE_BUNDLE, "bpass", "newpass", None)


def test_cmd_share_export_propagates_error(mock_share_fns):
    mock_share_fns["export"].side_effect = ShareError("vault missing")
    with pytest.raises(ShareError, match="vault missing"):
        cmd_share_export("ghost", "pass", "bpass")
