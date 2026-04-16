import pytest
from unittest.mock import patch
from envault.cli_secrets import cmd_scan_secrets


SAMPLE_REPORT = {
    "vault": "prod",
    "total": 4,
    "sensitive_count": 2,
    "safe_count": 2,
    "sensitive_keys": ["API_KEY", "SECRET"],
    "safe_keys": ["APP_NAME", "PORT"],
}


@pytest.fixture
def mock_scan():
    with patch("envault.cli_secrets.scan_secrets", return_value=SAMPLE_REPORT) as m:
        yield m


def test_cmd_scan_ok(mock_scan):
    result = cmd_scan_secrets("prod", "pass")
    assert result["ok"] is True
    assert result["report"] == SAMPLE_REPORT


def test_cmd_scan_includes_formatted_by_default(mock_scan):
    result = cmd_scan_secrets("prod", "pass")
    assert "formatted" in result
    assert isinstance(result["formatted"], str)


def test_cmd_scan_raw_skips_formatted(mock_scan):
    result = cmd_scan_secrets("prod", "pass", raw=True)
    assert "formatted" not in result


def test_cmd_scan_error_on_missing_vault():
    from envault.env_secrets import SecretsError
    with patch("envault.cli_secrets.scan_secrets", side_effect=SecretsError("not found")):
        result = cmd_scan_secrets("ghost", "pass")
    assert result["ok"] is False
    assert "not found" in result["error"]
