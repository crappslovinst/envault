import pytest
from unittest.mock import patch
from envault.env_mask import mask_env, _mask_value, format_mask_result, count_masked, MaskError


ENV = {
    "API_KEY": "supersecret",
    "DB_PASSWORD": "hunter2",
    "APP_NAME": "myapp",
    "PORT": "8080",
}


@pytest.fixture
def mock_get_env():
    with patch("envault.env_mask.get_env_vars", return_value=dict(ENV)) as m:
        yield m


def test_mask_hides_sensitive_keys(mock_get_env):
    result = mask_env("myvault", "pass")
    assert result["API_KEY"] != "supersecret"
    assert result["DB_PASSWORD"] != "hunter2"


def test_mask_keeps_non_sensitive_keys(mock_get_env):
    result = mask_env("myvault", "pass")
    assert result["APP_NAME"] == "myapp"
    assert result["PORT"] == "8080"


def test_mask_show_partial(mock_get_env):
    result = mask_env("myvault", "pass", show_partial=True)
    val = result["API_KEY"]
    assert val.startswith("su")
    assert val.endswith("et")
    assert "*" in val


def test_mask_specific_keys_only(mock_get_env):
    result = mask_env("myvault", "pass", keys=["API_KEY"])
    assert result["API_KEY"] != "supersecret"
    assert result["DB_PASSWORD"] == "hunter2"  # not in keys list, skipped


def test_mask_raises_on_bad_vault():
    with patch("envault.env_mask.get_env_vars", side_effect=Exception("not found")):
        with pytest.raises(MaskError, match="not found"):
            mask_env("ghost", "pass")


def test_mask_value_full():
    assert _mask_value("secret") == "******"


def test_mask_value_empty():
    assert _mask_value("") == "****"


def test_mask_value_partial_short():
    # value too short for partial reveal
    val = _mask_value("ab", show_partial=True)
    assert "*" in val


def test_format_mask_result(mock_get_env):
    masked = mask_env("myvault", "pass")
    out = format_mask_result(masked)
    assert "APP_NAME=myapp" in out
    assert "PORT=8080" in out


def test_count_masked(mock_get_env):
    original = dict(ENV)
    masked = mask_env("myvault", "pass")
    n = count_masked(masked, original)
    assert n >= 2
