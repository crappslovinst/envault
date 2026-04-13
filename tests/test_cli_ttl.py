"""Tests for envault/cli_ttl.py"""

from __future__ import annotations

import time
from unittest.mock import patch

import pytest

from envault.cli_ttl import (
    cmd_check_expired,
    cmd_clear_ttl,
    cmd_get_ttl,
    cmd_set_ttl,
    format_ttl_info,
)

VAULT = "myvault"
PASSWORD = "pass"


def test_cmd_set_ttl_returns_ok():
    with patch("envault.cli_ttl.set_ttl", return_value={"vault": VAULT, "ttl_seconds": 60, "expires_at": 9999.0}) as mock:
        result = cmd_set_ttl(VAULT, PASSWORD, 60)
    assert result["status"] == "ok"
    assert "TTL" in result["message"]
    mock.assert_called_once_with(VAULT, PASSWORD, 60)


def test_cmd_get_ttl_no_ttl():
    with patch("envault.cli_ttl.get_ttl", return_value=None):
        result = cmd_get_ttl(VAULT, PASSWORD)
    assert result["ttl"] is None
    assert "No TTL" in result["message"]


def test_cmd_get_ttl_active():
    fake_info = {
        "vault": VAULT,
        "ttl_seconds": 300,
        "expires_at": time.time() + 300,
        "remaining_seconds": 298.5,
        "expired": False,
    }
    with patch("envault.cli_ttl.get_ttl", return_value=fake_info):
        result = cmd_get_ttl(VAULT, PASSWORD)
    assert result["ttl_status"] == "active"
    assert result["remaining_seconds"] == 298.5


def test_cmd_get_ttl_expired():
    fake_info = {
        "vault": VAULT,
        "ttl_seconds": 10,
        "expires_at": time.time() - 5,
        "remaining_seconds": 0,
        "expired": True,
    }
    with patch("envault.cli_ttl.get_ttl", return_value=fake_info):
        result = cmd_get_ttl(VAULT, PASSWORD)
    assert result["ttl_status"] == "expired"


def test_cmd_clear_ttl_cleared():
    with patch("envault.cli_ttl.clear_ttl", return_value={"vault": VAULT, "ttl_cleared": True}):
        result = cmd_clear_ttl(VAULT, PASSWORD)
    assert "cleared" in result["message"].lower()


def test_cmd_clear_ttl_nothing_to_clear():
    with patch("envault.cli_ttl.clear_ttl", return_value={"vault": VAULT, "ttl_cleared": False}):
        result = cmd_clear_ttl(VAULT, PASSWORD)
    assert "No TTL" in result["message"]


def test_cmd_check_expired_false():
    with patch("envault.cli_ttl.is_expired", return_value=False):
        result = cmd_check_expired(VAULT, PASSWORD)
    assert result["expired"] is False
    assert "valid" in result["message"]


def test_cmd_check_expired_true():
    with patch("envault.cli_ttl.is_expired", return_value=True):
        result = cmd_check_expired(VAULT, PASSWORD)
    assert result["expired"] is True
    assert "expired" in result["message"]


def test_format_ttl_info_no_ttl():
    info = {"vault": VAULT, "ttl": None}
    out = format_ttl_info(info)
    assert "no TTL" in out


def test_format_ttl_info_active():
    info = {"vault": VAULT, "ttl": 300, "ttl_status": "active", "remaining_seconds": 200}
    out = format_ttl_info(info)
    assert "active" in out
    assert "200s" in out
