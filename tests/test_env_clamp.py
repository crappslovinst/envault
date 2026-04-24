"""Tests for envault.env_clamp."""

import pytest
from unittest.mock import patch, MagicMock

from envault.env_clamp import ClampError, clamp_values, format_clamp_result


@pytest.fixture()
def mock_clamp_deps():
    env_data = {
        "SHORT": "hi",
        "EXACT": "hello",
        "TOOLONG": "this_is_way_too_long_value",
    }
    with (
        patch("envault.env_clamp.vault_exists", return_value=True) as _exists,
        patch("envault.env_clamp.get_env_vars", return_value=dict(env_data)) as _get,
        patch("envault.env_clamp.push_env") as _push,
    ):
        yield {"exists": _exists, "get": _get, "push": _push, "env": env_data}


def test_clamp_raises_if_vault_missing():
    with patch("envault.env_clamp.vault_exists", return_value=False):
        with pytest.raises(ClampError, match="not found"):
            clamp_values("ghost", "pw")


def test_clamp_raises_on_invalid_min_max(mock_clamp_deps):
    with pytest.raises(ClampError, match="min_len must be"):
        clamp_values("v", "pw", min_len=10, max_len=5)


def test_clamp_raises_on_negative_lengths(mock_clamp_deps):
    with pytest.raises(ClampError, match="non-negative"):
        clamp_values("v", "pw", min_len=-1)


def test_clamp_raises_on_bad_pad_char(mock_clamp_deps):
    with pytest.raises(ClampError, match="one character"):
        clamp_values("v", "pw", pad_char="ab")


def test_clamp_pads_short_values(mock_clamp_deps):
    result = clamp_values("v", "pw", min_len=5, max_len=30)
    assert "SHORT" in result["padded"]
    assert "EXACT" not in result["padded"]


def test_clamp_truncates_long_values(mock_clamp_deps):
    result = clamp_values("v", "pw", min_len=0, max_len=10)
    assert "TOOLONG" in result["truncated"]
    assert "SHORT" not in result["truncated"]


def test_clamp_calls_push_when_changed(mock_clamp_deps):
    clamp_values("v", "pw", min_len=5, max_len=10)
    mock_clamp_deps["push"].assert_called_once()


def test_clamp_dry_run_skips_push(mock_clamp_deps):
    result = clamp_values("v", "pw", min_len=5, max_len=10, dry_run=True)
    mock_clamp_deps["push"].assert_not_called()
    assert result["dry_run"] is True


def test_clamp_no_change_skips_push(mock_clamp_deps):
    # All values fit within generous bounds
    result = clamp_values("v", "pw", min_len=0, max_len=9999)
    mock_clamp_deps["push"].assert_not_called()
    assert result["changed"] is False


def test_clamp_result_keys(mock_clamp_deps):
    result = clamp_values("v", "pw")
    for key in ("vault", "min_len", "max_len", "total", "padded", "truncated", "changed", "dry_run"):
        assert key in result


def test_format_clamp_result_contains_vault(mock_clamp_deps):
    result = clamp_values("myvault", "pw", min_len=5, max_len=20)
    formatted = format_clamp_result(result)
    assert "myvault" in formatted
    assert "Range" in formatted


def test_format_clamp_result_dry_run_note(mock_clamp_deps):
    result = clamp_values("v", "pw", min_len=5, max_len=20, dry_run=True)
    formatted = format_clamp_result(result)
    assert "dry run" in formatted
