import pytest
from unittest.mock import patch, MagicMock
from envault.cli_diff_keys import cmd_diff_keys
from envault.env_diff_keys import DiffKeysError


SAMPLE_RESULT = {
    "vault_a": "va",
    "vault_b": "vb",
    "only_in_a": ["KEY_X"],
    "only_in_b": ["KEY_Y"],
    "in_both": ["SHARED"],
    "total_a": 2,
    "total_b": 2,
    "shared": 1,
    "unique_to_a": 1,
    "unique_to_b": 1,
}


@pytest.fixture
def mock_diff_keys():
    with patch("envault.cli_diff_keys.diff_keys", return_value=SAMPLE_RESULT) as m:
        yield m


def test_cmd_diff_keys_ok(mock_diff_keys):
    result = cmd_diff_keys("va", "pw", "vb", "pw")
    assert result["ok"] is True
    assert result["shared"] == 1


def test_cmd_diff_keys_includes_formatted_by_default(mock_diff_keys):
    with patch("envault.cli_diff_keys.format_diff_keys_result", return_value="formatted"):
        result = cmd_diff_keys("va", "pw", "vb", "pw")
    assert "formatted" in result
    assert result["formatted"] == "formatted"


def test_cmd_diff_keys_raw_skips_formatted(mock_diff_keys):
    result = cmd_diff_keys("va", "pw", "vb", "pw", raw=True)
    assert "formatted" not in result


def test_cmd_diff_keys_error_on_missing_vault():
    with patch("envault.cli_diff_keys.diff_keys", side_effect=DiffKeysError("Vault not found: va")):
        result = cmd_diff_keys("va", "pw", "vb", "pw")
    assert result["ok"] is False
    assert "va" in result["error"]


def test_cmd_diff_keys_passes_passwords(mock_diff_keys):
    cmd_diff_keys("va", "pass1", "vb", "pass2")
    mock_diff_keys.assert_called_once_with("va", "pass1", "vb", "pass2")
