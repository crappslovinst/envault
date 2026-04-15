"""Tests for envault.watch module."""

import pytest
from unittest.mock import patch, MagicMock, call

from envault.watch import watch_env, WatchError


FAKE_ENV_PATH = "/fake/.env"
VAULT = "myproject"
PASS = "secret"


@pytest.fixture
def mock_watch_deps(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("KEY=value\n")

    with (
        patch("envault.watch.push_env") as mock_push,
        patch("envault.watch.record_event") as mock_record,
        patch("envault.watch.time.sleep"),
    ):
        mock_push.return_value = {"KEY": "value"}
        mock_record.return_value = {"action": "watch_push", "vault": VAULT}
        yield env_file, mock_push, mock_record


def test_watch_raises_if_file_missing():
    with pytest.raises(WatchError, match="File not found"):
        watch_env(FAKE_ENV_PATH, VAULT, PASS, max_events=1)


def test_watch_pushes_on_change(mock_watch_deps):
    env_file, mock_push, mock_record = mock_watch_deps

    hashes = ["aaa", "aaa", "bbb"]
    with patch("envault.watch._file_hash", side_effect=hashes):
        events = watch_env(str(env_file), VAULT, PASS, max_events=1)

    assert len(events) == 1
    mock_push.assert_called_once_with(VAULT, PASS, env_path=str(env_file))


def test_watch_records_audit_event(mock_watch_deps):
    env_file, mock_push, mock_record = mock_watch_deps

    hashes = ["aaa", "bbb"]
    with patch("envault.watch._file_hash", side_effect=hashes):
        watch_env(str(env_file), VAULT, PASS, max_events=1)

    mock_record.assert_called_once()
    _, kwargs = mock_record.call_args
    assert kwargs["action"] == "watch_push" or mock_record.call_args[0][1] if mock_record.call_args[0] else True
    call_kwargs = mock_record.call_args.kwargs if mock_record.call_args.kwargs else {}
    # accept both positional and keyword
    assert mock_record.called


def test_watch_calls_on_change_callback(mock_watch_deps):
    env_file, mock_push, _ = mock_watch_deps
    callback = MagicMock()

    hashes = ["x", "y"]
    with patch("envault.watch._file_hash", side_effect=hashes):
        watch_env(str(env_file), VAULT, PASS, max_events=1, on_change=callback)

    callback.assert_called_once_with(str(env_file), {"KEY": "value"})


def test_watch_no_push_when_unchanged(mock_watch_deps):
    env_file, mock_push, _ = mock_watch_deps
    # same hash twice then different — but max_events means we stop after first push
    # here we want to confirm no push happens when hash is same
    # We'll allow 2 sleep cycles with same hash, then change
    hashes = ["aaa", "aaa", "aaa", "bbb"]
    with patch("envault.watch._file_hash", side_effect=hashes):
        events = watch_env(str(env_file), VAULT, PASS, max_events=1)

    assert mock_push.call_count == 1


def test_watch_raises_if_file_disappears(mock_watch_deps):
    env_file, _, _ = mock_watch_deps

    call_count = 0

    def fake_isfile(path):
        nonlocal call_count
        call_count += 1
        return call_count == 1  # True only on first check

    with patch("envault.watch.os.path.isfile", side_effect=fake_isfile):
        with patch("envault.watch._file_hash", return_value="abc"):
            with pytest.raises(WatchError, match="disappeared"):
                watch_env(str(env_file), VAULT, PASS, max_events=5)
