import pytest
from unittest.mock import patch, MagicMock
from envault.env_truncate import truncate_values, format_truncate_result, TruncateError

SAMPLE_ENV = {
    "SHORT": "hi",
    "LONG_KEY": "a" * 100,
    "EXACT": "b" * 64,
    "OVER": "c" * 80,
}


@pytest.fixture
def mock_deps():
    with patch("envault.env_truncate.get_env_vars") as _get, \
         patch("envault.env_truncate.push_env") as _push:
        _get.return_value = dict(SAMPLE_ENV)
        yield _get, _push


def test_truncate_returns_summary(mock_deps):
    _get, _push = mock_deps
    result = truncate_values("myvault", "pass")
    assert result["vault"] == "myvault"
    assert result["max_length"] == 64
    assert isinstance(result["truncated_keys"], list)


def test_truncate_detects_long_values(mock_deps):
    _get, _push = mock_deps
    result = truncate_values("myvault", "pass", max_length=64)
    assert "LONG_KEY" in result["truncated_keys"]
    assert "OVER" in result["truncated_keys"]


def test_truncate_leaves_short_values(mock_deps):
    _get, _push = mock_deps
    result = truncate_values("myvault", "pass", max_length=64)
    assert "SHORT" not in result["truncated_keys"]
    assert "EXACT" not in result["truncated_keys"]


def test_truncate_values_are_capped(mock_deps):
    _get, _push = mock_deps
    result = truncate_values("myvault", "pass", max_length=64)
    for k in result["truncated_keys"]:
        assert len(result["result"][k]) == 64


def test_truncate_calls_push_when_changed(mock_deps):
    _get, _push = mock_deps
    truncate_values("myvault", "pass", max_length=64)
    _push.assert_called_once()


def test_truncate_dry_run_skips_push(mock_deps):
    _get, _push = mock_deps
    result = truncate_values("myvault", "pass", max_length=64, dry_run=True)
    _push.assert_not_called()
    assert result["dry_run"] is True


def test_truncate_invalid_max_length(mock_deps):
    _get, _push = mock_deps
    with pytest.raises(TruncateError):
        truncate_values("myvault", "pass", max_length=0)


def test_truncate_raises_on_bad_vault():
    with patch("envault.env_truncate.get_env_vars", side_effect=Exception("not found")):
        with pytest.raises(TruncateError, match="not found"):
            truncate_values("missing", "pass")


def test_format_truncate_result(mock_deps):
    _get, _push = mock_deps
    result = truncate_values("myvault", "pass", max_length=64)
    output = format_truncate_result(result)
    assert "myvault" in output
    assert "64" in output
    assert "LONG_KEY" in output or "OVER" in output


def test_format_dry_run_note(mock_deps):
    _get, _push = mock_deps
    result = truncate_values("myvault", "pass", max_length=64, dry_run=True)
    output = format_truncate_result(result)
    assert "dry run" in output
