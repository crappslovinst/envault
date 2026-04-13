"""Tests for envault/template.py"""

import pytest
from unittest.mock import patch, MagicMock
from envault.template import generate_template, save_template, TemplateError


SAMPLE_VARS = {
    "APP_ENV": "production",
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "SECRET_KEY": "supersecret",
}


@pytest.fixture
def mock_get_env():
    with patch("envault.template.get_env_vars", return_value=SAMPLE_VARS) as m:
        yield m


def test_generate_template_blanks_values(mock_get_env):
    result = generate_template("myvault", "pass")
    assert "APP_ENV=" in result
    assert "production" not in result


def test_generate_template_includes_all_keys(mock_get_env):
    result = generate_template("myvault", "pass")
    for key in SAMPLE_VARS:
        assert key in result


def test_generate_template_custom_placeholder(mock_get_env):
    result = generate_template("myvault", "pass", placeholder="CHANGEME")
    assert "APP_ENV=CHANGEME" in result
    assert "DB_HOST=CHANGEME" in result


def test_generate_template_include_values(mock_get_env):
    result = generate_template("myvault", "pass", include_values=True)
    assert "APP_ENV=production" in result
    assert "SECRET_KEY=supersecret" in result


def test_generate_template_prefix_filter(mock_get_env):
    result = generate_template("myvault", "pass", prefix_filter="DB_")
    assert "DB_HOST=" in result
    assert "DB_PORT=" in result
    assert "APP_ENV" not in result
    assert "SECRET_KEY" not in result


def test_generate_template_keys_sorted(mock_get_env):
    result = generate_template("myvault", "pass")
    keys_in_output = [line.split("=")[0] for line in result.splitlines() if "=" in line]
    assert keys_in_output == sorted(keys_in_output)


def test_generate_template_has_header(mock_get_env):
    result = generate_template("myvault", "pass")
    assert "# Template generated from vault: myvault" in result


def test_generate_template_raises_on_bad_vault():
    with patch("envault.template.get_env_vars", side_effect=Exception("not found")):
        with pytest.raises(TemplateError, match="Could not read vault"):
            generate_template("missing", "pass")


def test_save_template_writes_file(tmp_path):
    out = tmp_path / "template.env"
    save_template("KEY=VALUE\n", str(out))
    assert out.read_text() == "KEY=VALUE\n"


def test_save_template_raises_on_bad_path():
    with pytest.raises(TemplateError, match="Could not write template"):
        save_template("KEY=VALUE", "/nonexistent_dir/template.env")
