"""Tests for envault.cli_audit module."""

import pytest

from envault.audit import record_event
from envault.cli_audit import cmd_log, cmd_clear_log, format_event


@pytest.fixture
def tmp_audit_dir(tmp_path):
    return str(tmp_path)


def test_cmd_log_returns_events(tmp_audit_dir):
    record_event("push", "myapp", vault_dir=tmp_audit_dir)
    events = cmd_log(vault_dir=tmp_audit_dir)
    assert len(events) == 1
    assert events[0]["action"] == "push"


def test_cmd_log_most_recent_first(tmp_audit_dir):
    record_event("push", "myapp", vault_dir=tmp_audit_dir)
    record_event("pull", "myapp", vault_dir=tmp_audit_dir)
    events = cmd_log(vault_dir=tmp_audit_dir)
    assert events[0]["action"] == "pull"
    assert events[1]["action"] == "push"


def test_cmd_log_respects_limit(tmp_audit_dir):
    for i in range(10):
        record_event("push", f"app{i}", vault_dir=tmp_audit_dir)
    events = cmd_log(limit=3, vault_dir=tmp_audit_dir)
    assert len(events) == 3


def test_cmd_log_filters_by_vault(tmp_audit_dir):
    record_event("push", "alpha", vault_dir=tmp_audit_dir)
    record_event("push", "beta", vault_dir=tmp_audit_dir)
    events = cmd_log(vault_name="alpha", vault_dir=tmp_audit_dir)
    assert all(e["vault"] == "alpha" for e in events)


def test_cmd_log_empty(tmp_audit_dir):
    events = cmd_log(vault_dir=tmp_audit_dir)
    assert events == []


def test_cmd_clear_log(tmp_audit_dir):
    record_event("push", "myapp", vault_dir=tmp_audit_dir)
    msg = cmd_clear_log(vault_dir=tmp_audit_dir)
    assert "cleared" in msg.lower()
    assert cmd_log(vault_dir=tmp_audit_dir) == []


def test_format_event_basic():
    event = {
        "timestamp": "2024-01-01T00:00:00+00:00",
        "action": "push",
        "vault": "myapp",
        "user": "alice",
        "extra": {},
    }
    line = format_event(event)
    assert "push" in line.upper()
    assert "myapp" in line
    assert "alice" in line


def test_format_event_with_extra():
    event = {
        "timestamp": "2024-01-01T00:00:00+00:00",
        "action": "push",
        "vault": "myapp",
        "user": "bob",
        "extra": {"keys": 7},
    }
    line = format_event(event)
    assert "keys=7" in line
