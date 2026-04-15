"""Tests for envault/remind.py and envault/cli_remind.py."""

from __future__ import annotations

import time
import pytest
from unittest.mock import patch, MagicMock

from envault.remind import (
    RemindError,
    set_rotation_reminder,
    get_reminders,
    check_due,
    clear_reminder,
)
from envault.cli_remind import (
    cmd_set_reminder,
    cmd_check_reminders,
    cmd_list_reminders,
    cmd_clear_reminder,
    format_due_list,
)

VAULT = "myvault"
PASS = "secret"


@pytest.fixture()
def mock_remind_deps():
    _store: dict = {}

    def _exists(name):
        return name in _store

    def _load(name, pw):
        return dict(_store.get(name, {}))

    def _save(name, pw, data):
        _store[name] = dict(data)

    with (
        patch("envault.remind.vault_exists", side_effect=_exists),
        patch("envault.remind.load_vault", side_effect=_load),
        patch("envault.remind.save_vault", side_effect=_save),
    ):
        _store[VAULT] = {}
        yield _store


def test_set_reminder_returns_summary(mock_remind_deps):
    result = set_rotation_reminder(VAULT, "DB_PASSWORD", PASS, 30)
    assert result["vault"] == VAULT
    assert result["key"] == "DB_PASSWORD"
    assert result["interval_days"] == 30


def test_set_reminder_persists(mock_remind_deps):
    set_rotation_reminder(VAULT, "API_KEY", PASS, 7)
    reminders = get_reminders(VAULT, PASS)
    assert "API_KEY" in reminders
    assert reminders["API_KEY"]["interval_days"] == 7


def test_set_reminder_raises_if_vault_missing(mock_remind_deps):
    with pytest.raises(RemindError, match="not found"):
        set_rotation_reminder("ghost", "KEY", PASS, 10)


def test_check_due_empty_when_fresh(mock_remind_deps):
    set_rotation_reminder(VAULT, "SECRET", PASS, 30)
    due = check_due(VAULT, PASS)
    assert due == []


def test_check_due_detects_overdue(mock_remind_deps):
    set_rotation_reminder(VAULT, "OLD_KEY", PASS, 1)
    # backdate last_rotated by 2 days
    data = mock_remind_deps[VAULT]
    data["__reminders__"]["OLD_KEY"]["last_rotated"] -= 2 * 86400
    due = check_due(VAULT, PASS)
    assert any(d["key"] == "OLD_KEY" for d in due)


def test_clear_reminder_removes_key(mock_remind_deps):
    set_rotation_reminder(VAULT, "TMP_KEY", PASS, 14)
    clear_reminder(VAULT, "TMP_KEY", PASS)
    reminders = get_reminders(VAULT, PASS)
    assert "TMP_KEY" not in reminders


def test_clear_reminder_raises_if_key_missing(mock_remind_deps):
    with pytest.raises(RemindError, match="No reminder"):
        clear_reminder(VAULT, "NONEXISTENT", PASS)


def test_cmd_set_reminder_ok(mock_remind_deps):
    result = cmd_set_reminder(VAULT, "DB_PASS", PASS, 30)
    assert result["ok"] is True
    assert result["key"] == "DB_PASS"


def test_cmd_check_reminders_no_due(mock_remind_deps):
    result = cmd_check_reminders(VAULT, PASS)
    assert result["ok"] is True
    assert result["count"] == 0


def test_cmd_list_reminders_returns_dict(mock_remind_deps):
    set_rotation_reminder(VAULT, "X", PASS, 5)
    result = cmd_list_reminders(VAULT, PASS)
    assert result["ok"] is True
    assert "X" in result["reminders"]


def test_format_due_list_empty():
    assert format_due_list([]) == "All keys are up to date."


def test_format_due_list_shows_key():
    due = [{"key": "API_KEY", "interval_days": 7, "elapsed_days": 10.5}]
    output = format_due_list(due)
    assert "API_KEY" in output
    assert "overdue" in output
