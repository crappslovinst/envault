"""Tests for envault.audit module."""

import pytest
from pathlib import Path

from envault.audit import record_event, get_events, clear_events


@pytest.fixture
def tmp_audit_dir(tmp_path):
    return str(tmp_path)


def test_record_event_returns_dict(tmp_audit_dir):
    event = record_event("push", "myapp", vault_dir=tmp_audit_dir)
    assert event["action"] == "push"
    assert event["vault"] == "myapp"
    assert "timestamp" in event
    assert "user" in event


def test_record_event_persists(tmp_audit_dir):
    record_event("push", "myapp", vault_dir=tmp_audit_dir)
    events = get_events(vault_dir=tmp_audit_dir)
    assert len(events) == 1
    assert events[0]["action"] == "push"


def test_multiple_events_accumulate(tmp_audit_dir):
    record_event("push", "myapp", vault_dir=tmp_audit_dir)
    record_event("pull", "myapp", vault_dir=tmp_audit_dir)
    record_event("push", "otherapp", vault_dir=tmp_audit_dir)
    events = get_events(vault_dir=tmp_audit_dir)
    assert len(events) == 3


def test_get_events_filtered_by_vault(tmp_audit_dir):
    record_event("push", "myapp", vault_dir=tmp_audit_dir)
    record_event("pull", "otherapp", vault_dir=tmp_audit_dir)
    events = get_events(vault_name="myapp", vault_dir=tmp_audit_dir)
    assert len(events) == 1
    assert events[0]["vault"] == "myapp"


def test_get_events_empty_when_no_file(tmp_audit_dir):
    events = get_events(vault_dir=tmp_audit_dir)
    assert events == []


def test_record_event_with_extra(tmp_audit_dir):
    event = record_event(
        "push", "myapp", extra={"keys": 5}, vault_dir=tmp_audit_dir
    )
    assert event["extra"]["keys"] == 5
    stored = get_events(vault_dir=tmp_audit_dir)
    assert stored[0]["extra"]["keys"] == 5


def test_clear_events(tmp_audit_dir):
    record_event("push", "myapp", vault_dir=tmp_audit_dir)
    clear_events(vault_dir=tmp_audit_dir)
    assert get_events(vault_dir=tmp_audit_dir) == []


def test_record_event_custom_user(tmp_audit_dir):
    event = record_event("pull", "myapp", user="alice", vault_dir=tmp_audit_dir)
    assert event["user"] == "alice"
