import pytest
from unittest.mock import patch
from envault.env_sample import generate_sample, save_sample, format_sample_result, SampleError


SAMPLE_ENV = {
    "APP_NAME": "myapp",
    "SECRET_KEY": "supersecret",
    "DATABASE_URL": "postgres://localhost/db",
    "API_TOKEN": "tok_abc123",
    "DEBUG": "true",
}


@pytest.fixture
def mock_get_env():
    with patch("envault.env_sample.get_env_vars", return_value=SAMPLE_ENV) as m:
        yield m


def test_generate_sample_masks_sensitive(mock_get_env):
    result = generate_sample("myvault", "pass")
    assert result["sample"]["SECRET_KEY"] == ""
    assert result["sample"]["API_TOKEN"] == ""


def test_generate_sample_blanks_all_by_default(mock_get_env):
    result = generate_sample("myvault", "pass")
    # non-sensitive keys are also blanked when mask_sensitive=True and include_values=False
    assert result["sample"]["APP_NAME"] == ""
    assert result["sample"]["DEBUG"] == ""


def test_generate_sample_include_values(mock_get_env):
    result = generate_sample("myvault", "pass", include_values=True)
    assert result["sample"]["APP_NAME"] == "myapp"
    assert result["sample"]["SECRET_KEY"] == "supersecret"


def test_generate_sample_custom_placeholder(mock_get_env):
    result = generate_sample("myvault", "pass", placeholder="CHANGEME")
    assert result["sample"]["SECRET_KEY"] == "CHANGEME"


def test_generate_sample_total(mock_get_env):
    result = generate_sample("myvault", "pass")
    assert result["total"] == len(SAMPLE_ENV)


def test_generate_sample_masked_count(mock_get_env):
    result = generate_sample("myvault", "pass", placeholder="")
    assert result["masked"] == len(SAMPLE_ENV)


def test_generate_sample_raises_on_bad_vault():
    with patch("envault.env_sample.get_env_vars", side_effect=Exception("not found")):
        with pytest.raises(SampleError, match="not found"):
            generate_sample("ghost", "pass")


def test_save_sample_writes_file(mock_get_env, tmp_path):
    result = generate_sample("myvault", "pass", placeholder="")
    out = tmp_path / ".env.sample"
    path = save_sample(result, str(out))
    assert out.exists()
    content = out.read_text()
    for key in SAMPLE_ENV:
        assert key in content


def test_format_sample_result_contains_vault_name(mock_get_env):
    result = generate_sample("myvault", "pass")
    formatted = format_sample_result(result)
    assert "myvault" in formatted
    assert "Total" in formatted
    assert "Masked" in formatted
