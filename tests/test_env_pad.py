import pytest
from unittest.mock import patch, MagicMock
from envault.env_pad import pad_values, format_pad_result, PadError


@pytest.fixture
def mock_pad_deps():
    with patch("envault.env_pad.vault_exists") as _exists, \
         patch("envault.env_pad.get_env_vars") as _get, \
         patch("envault.env_pad.push_env") as _push:
        _exists.return_value = True
        _get.return_value = {"PORT": "80", "TIMEOUT": "3000", "NAME": "app"}
        yield _exists, _get, _push


def test_pad_values_raises_if_vault_missing():
    with patch("envault.env_pad.vault_exists", return_value=False):
        with pytest.raises(PadError, match="not found"):
            pad_values("ghost", "pass", 4)


def test_pad_values_raises_on_bad_fill_char(mock_pad_deps):
    with pytest.raises(PadError, match="fill_char"):
        pad_values("v", "p", 5, fill_char="ab")


def test_pad_values_raises_on_zero_min_length(mock_pad_deps):
    with pytest.raises(PadError, match="min_length"):
        pad_values("v", "p", 0)


def test_pad_values_pads_short_values(mock_pad_deps):
    _, _get, _push = mock_pad_deps
    _get.return_value = {"PORT": "80", "CODE": "42"}
    result = pad_values("v", "p", 4, fill_char="0")
    assert result["padded"]["PORT"] == "8000"
    assert result["padded"]["CODE"] == "4200"


def test_pad_values_skips_long_enough_values(mock_pad_deps):
    _, _get, _ = mock_pad_deps
    _get.return_value = {"TIMEOUT": "3000", "X": "1"}
    result = pad_values("v", "p", 4)
    assert "TIMEOUT" in result["skipped"]
    assert "X" not in result["skipped"]


def test_pad_values_respects_keys_filter(mock_pad_deps):
    _, _get, _push = mock_pad_deps
    _get.return_value = {"A": "1", "B": "2", "C": "100"}
    result = pad_values("v", "p", 4, keys=["A"])
    assert "A" in result["padded"]
    assert "B" not in result["padded"]
    assert "C" not in result["padded"]


def test_pad_values_dry_run_skips_push(mock_pad_deps):
    _, _get, _push = mock_pad_deps
    _get.return_value = {"X": "1"}
    result = pad_values("v", "p", 5, dry_run=True)
    _push.assert_not_called()
    assert result["dry_run"] is True


def test_pad_values_calls_push_when_changed(mock_pad_deps):
    _, _get, _push = mock_pad_deps
    _get.return_value = {"X": "1"}
    pad_values("v", "p", 5)
    _push.assert_called_once()


def test_format_pad_result_shows_padded():
    result = {
        "vault": "myv",
        "padded": {"PORT": "8000"},
        "skipped": [],
        "total_padded": 1,
        "dry_run": False,
    }
    out = format_pad_result(result)
    assert "PORT" in out
    assert "8000" in out


def test_format_pad_result_dry_run_note():
    result = {
        "vault": "myv",
        "padded": {},
        "skipped": [],
        "total_padded": 0,
        "dry_run": True,
    }
    out = format_pad_result(result)
    assert "dry run" in out
