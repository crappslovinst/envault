import pytest
from unittest.mock import patch
from envault.env_secrets import scan_secrets, format_secrets_report, SecretsError, _is_sensitive


SAMPLE_ENV = {
    "DATABASE_URL": "postgres://localhost/db",
    "API_KEY": "abc123",
    "SECRET_TOKEN": "s3cr3t",
    "APP_NAME": "myapp",
    "AWS_ACCESS_KEY": "AKIA...",
    "PORT": "8080",
}


@pytest.fixture
def mock_get_env():
    with patch("envault.env_secrets.get_env_vars", return_value=SAMPLE_ENV) as m:
        yield m


def test_is_sensitive_detects_common_patterns():
    assert _is_sensitive("API_KEY") is True
    assert _is_sensitive("SECRET_TOKEN") is True
    assert _is_sensitive("DB_PASSWORD") is True
    assert _is_sensitive("PORT") is False
    assert _is_sensitive("APP_NAME") is False


def test_scan_returns_correct_counts(mock_get_env):
    report = scan_secrets("myenv", "pass")
    assert report["total"] == 6
    assert report["sensitive_count"] == 3
    assert report["safe_count"] == 3


def test_scan_sensitive_keys_sorted(mock_get_env):
    report = scan_secrets("myenv", "pass")
    assert report["sensitive_keys"] == sorted(report["sensitive_keys"])


def test_scan_safe_keys_sorted(mock_get_env):
    report = scan_secrets("myenv", "pass")
    assert report["safe_keys"] == sorted(report["safe_keys"])


def test_scan_raises_on_bad_vault():
    with patch("envault.env_secrets.get_env_vars", side_effect=Exception("not found")):
        with pytest.raises(SecretsError, match="not found"):
            scan_secrets("missing", "pass")


def test_scan_vault_name_in_report(mock_get_env):
    report = scan_secrets("myenv", "pass")
    assert report["vault"] == "myenv"


def test_format_secrets_report_shows_sensitive(mock_get_env):
    report = scan_secrets("myenv", "pass")
    text = format_secrets_report(report)
    assert "Sensitive keys:" in text
    assert "API_KEY" in text


def test_format_secrets_report_no_sensitive():
    report = {
        "vault": "clean",
        "total": 2,
        "sensitive_count": 0,
        "safe_count": 2,
        "sensitive_keys": [],
        "safe_keys": ["APP_NAME", "PORT"],
    }
    text = format_secrets_report(report)
    assert "No sensitive keys detected." in text


def test_format_includes_vault_name(mock_get_env):
    report = scan_secrets("myenv", "pass")
    text = format_secrets_report(report)
    assert "myenv" in text
