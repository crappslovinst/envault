"""Tests for envault/env_extract.py"""

import pytest
from unittest.mock import patch, MagicMock

from envault.env_extract import extract_keys, format_extract_result, ExtractError


SRC = "src_vault"
DST = "dst_vault"
PASS = "pass"


@pytest.fixture
def mock_extract_deps():
    with patch("envault.env_extract.vault_exists") as mock_exists, \
         patch("envault.env_extract.get_env_vars") as mock_get, \
         patch("envault.env_extract.push_env") as mock_push:
        mock_exists.side_effect = lambda v: v == SRC
        mock_get.return_value = {"KEY_A": "val_a", "KEY_B": "val_b", "KEY_C": "val_c"}
        yield mock_exists, mock_get, mock_push


def test_extract_returns_summary(mock_extract_deps):
    result = extract_keys(SRC, PASS, DST, PASS, ["KEY_A", "KEY_B"])
    assert result["total_extracted"] == 2
    assert "KEY_A" in result["extracted"]
    assert result["missing"] == []


def test_extract_reports_missing_keys(mock_extract_deps):
    result = extract_keys(SRC, PASS, DST, PASS, ["KEY_A", "MISSING"])
    assert "MISSING" in result["missing"]
    assert result["total_extracted"] == 1


def test_extract_raises_if_src_missing():
    with patch("envault.env_extract.vault_exists", return_value=False):
        with pytest.raises(ExtractError, match="not found"):
            extract_keys(SRC, PASS, DST, PASS, ["KEY_A"])


def test_extract_raises_if_no_keys_found(mock_extract_deps):
    with pytest.raises(ExtractError, match="None of the requested"):
        extract_keys(SRC, PASS, DST, PASS, ["NONEXISTENT"])


def test_extract_calls_push(mock_extract_deps):
    _, _, mock_push = mock_extract_deps
    extract_keys(SRC, PASS, DST, PASS, ["KEY_A"])
    mock_push.assert_called_once()
    _, _, pushed_env = mock_push.call_args[0]
    assert "KEY_A" in pushed_env


def test_extract_overwrite_ignores_existing(mock_extract_deps):
    mock_exists, mock_get, mock_push = mock_extract_deps
    mock_exists.side_effect = lambda v: True  # both exist
    mock_get.return_value = {"KEY_A": "val_a"}
    result = extract_keys(SRC, PASS, DST, PASS, ["KEY_A"], overwrite=True)
    _, _, pushed_env = mock_push.call_args[0]
    assert pushed_env == {"KEY_A": "val_a"}


def test_format_extract_result():
    result = {
        "src_vault": "src",
        "dst_vault": "dst",
        "extracted": ["KEY_A"],
        "missing": ["KEY_Z"],
        "total_extracted": 1,
    }
    out = format_extract_result(result)
    assert "KEY_A" in out
    assert "KEY_Z" in out
    assert "src" in out
    assert "dst" in out
