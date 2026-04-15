"""Tests for envault.notes and envault.cli_notes."""

import pytest
from unittest.mock import patch, MagicMock

from envault.notes import add_note, get_notes, delete_note, clear_notes, NoteError
from envault.cli_notes import cmd_add_note, cmd_list_notes, cmd_delete_note, cmd_clear_notes

VAULT = "myvault"
PASS = "secret"


@pytest.fixture()
def mock_notes_deps():
    """Patch storage layer used by notes module."""
    store = {}

    def _exists(name):
        return name in store

    def _load(name, pw):
        return dict(store[name])

    def _save(name, data, pw):
        store[name] = dict(data)

    with patch("envault.notes.vault_exists", side_effect=_exists), \
         patch("envault.notes.load_vault", side_effect=_load), \
         patch("envault.notes.save_vault", side_effect=_save):
        yield store


# --- add_note ---

def test_add_note_raises_if_vault_missing(mock_notes_deps):
    with pytest.raises(NoteError, match="not found"):
        add_note(VAULT, PASS, "hello")


def test_add_note_returns_entry(mock_notes_deps):
    mock_notes_deps[VAULT] = {}
    entry = add_note(VAULT, PASS, "first note")
    assert entry["text"] == "first note"
    assert "ts" in entry


def test_add_note_persists(mock_notes_deps):
    mock_notes_deps[VAULT] = {}
    add_note(VAULT, PASS, "note one")
    add_note(VAULT, PASS, "note two")
    notes = get_notes(VAULT, PASS)
    assert len(notes) == 2
    assert notes[0]["text"] == "note one"
    assert notes[1]["text"] == "note two"


# --- get_notes ---

def test_get_notes_empty_by_default(mock_notes_deps):
    mock_notes_deps[VAULT] = {}
    assert get_notes(VAULT, PASS) == []


def test_get_notes_raises_if_vault_missing(mock_notes_deps):
    with pytest.raises(NoteError):
        get_notes(VAULT, PASS)


# --- delete_note ---

def test_delete_note_removes_correct_entry(mock_notes_deps):
    mock_notes_deps[VAULT] = {}
    add_note(VAULT, PASS, "alpha")
    add_note(VAULT, PASS, "beta")
    removed = delete_note(VAULT, PASS, 0)
    assert removed["text"] == "alpha"
    remaining = get_notes(VAULT, PASS)
    assert len(remaining) == 1
    assert remaining[0]["text"] == "beta"


def test_delete_note_raises_on_bad_index(mock_notes_deps):
    mock_notes_deps[VAULT] = {}
    add_note(VAULT, PASS, "only note")
    with pytest.raises(NoteError, match="out of range"):
        delete_note(VAULT, PASS, 5)


# --- clear_notes ---

def test_clear_notes_returns_count(mock_notes_deps):
    mock_notes_deps[VAULT] = {}
    add_note(VAULT, PASS, "a")
    add_note(VAULT, PASS, "b")
    count = clear_notes(VAULT, PASS)
    assert count == 2
    assert get_notes(VAULT, PASS) == []


# --- cli wrappers ---

def test_cmd_add_note_returns_ok(mock_notes_deps):
    mock_notes_deps[VAULT] = {}
    result = cmd_add_note(VAULT, PASS, "cli note")
    assert result["status"] == "ok"
    assert result["note"]["text"] == "cli note"


def test_cmd_list_notes_formatted(mock_notes_deps):
    mock_notes_deps[VAULT] = {}
    add_note(VAULT, PASS, "hello world")
    result = cmd_list_notes(VAULT, PASS)
    assert result["count"] == 1
    assert "hello world" in result["formatted"]


def test_cmd_list_notes_empty_message(mock_notes_deps):
    mock_notes_deps[VAULT] = {}
    result = cmd_list_notes(VAULT, PASS)
    assert result["formatted"] == "(no notes)"


def test_cmd_delete_note_returns_deleted(mock_notes_deps):
    mock_notes_deps[VAULT] = {}
    add_note(VAULT, PASS, "to delete")
    result = cmd_delete_note(VAULT, PASS, 0)
    assert result["status"] == "ok"
    assert result["deleted"]["text"] == "to delete"


def test_cmd_clear_notes_returns_count(mock_notes_deps):
    mock_notes_deps[VAULT] = {}
    add_note(VAULT, PASS, "x")
    result = cmd_clear_notes(VAULT, PASS)
    assert result["cleared"] == 1
    assert result["status"] == "ok"
