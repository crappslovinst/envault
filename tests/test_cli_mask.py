import pytest
from unittest.mock import patch
from envault.cli_mask import cmd_mask


MASKED = {
    "API_KEY": "********",
    "APP_NAME": "myapp",
}


@pytest.fixture
def mock_mask():
    with patch("envault.cli_mask.mask_env", return_value=dict(MASKED)) as m:
        yield m


def test_cmd_mask_ok(mock_mask):
    result = cmd_mask("myvault", "pass")
    assert result["ok"] is True
    assert result["vault"] == "myvault"
    assert result["masked"] == MASKED


def test_cmd_mask_includes_formatted_by_default(mock_mask):
    result = cmd_mask("myvault", "pass")
    assert "formatted" in result
    assert "APP_NAME=myapp" in result["formatted"]


def test_cmd_mask_raw_skips_formatted(mock_mask):
    result = cmd_mask("myvault", "pass", raw=True)
    assert "formatted" not in result


def test_cmd_mask_error_on_missing_vault():
    from envault.env_mask import MaskError
    with patch("envault.cli_mask.mask_env", side_effect=MaskError("vault not found")):
        result = cmd_mask("ghost", "pass")
    assert result["ok"] is False
    assert "not found" in result["error"]


def test_cmd_mask_passes_show_partial(mock_mask):
    cmd_mask("myvault", "pass", show_partial=True)
    mock_mask.assert_called_once_with("myvault", "pass", show_partial=True, keys=None)
