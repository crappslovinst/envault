"""Tests for envault.cli_count."""

from unittest.mock import patch

from envault.cli_count import cmd_count


MOCK_RESULT = {
    "vault": "myvault",
    "total": 3,
    "empty": 0,
    "non_empty": 3,
    "prefixes": {"APP": 2, "DB": 1},
}


def test_cmd_count_ok():
    with patch("envault.cli_count.count_keys", return_value=MOCK_RESULT):
        result = cmd_count("myvault", "pass")
    assert result["ok"] is True
    assert result["total"] == 3


def test_cmd_count_includes_formatted_by_default():
    with patch("envault.cli_count.count_keys", return_value=MOCK_RESULT):
        result = cmd_count("myvault", "pass")
    assert "formatted" in result
    assert isinstance(result["formatted"], str)


def test_cmd_count_raw_skips_formatted():
    with patch("envault.cli_count.count_keys", return_value=MOCK_RESULT):
        result = cmd_count("myvault", "pass", raw=True)
    assert "formatted" not in result


def test_cmd_count_error_on_missing_vault():
    from envault.env_count import CountError
    with patch("envault.cli_count.count_keys", side_effect=CountError("not found")):
        result = cmd_count("missing", "pass")
    assert result["ok"] is False
    assert "not found" in result["error"]


def test_cmd_count_prefixes_present():
    with patch("envault.cli_count.count_keys", return_value=MOCK_RESULT):
        result = cmd_count("myvault", "pass")
    assert result["prefixes"]["APP"] == 2
