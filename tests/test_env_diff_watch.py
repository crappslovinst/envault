"""Tests for envault.env_diff_watch."""

import pytest
from unittest.mock import patch, MagicMock
from envault.env_diff_watch import snapshot_diff, watch_diff, DiffWatchError


VAULT_ENV = {"KEY_A": "foo", "KEY_B": "bar"}
LOCAL_ENV_CHANGED = "KEY_A=foo\nKEY_B=changed\n"
LOCAL_ENV_SAME = "KEY_A=foo\nKEY_B=bar\n"
LOCAL_ENV_ADDED = "KEY_A=foo\nKEY_B=bar\nKEY_C=new\n"


@pytest.fixture()
def mock_deps(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(LOCAL_ENV_SAME)
    with patch("envault.env_diff_watch.get_env_vars", return_value=VAULT_ENV), \
         patch("envault.env_diff_watch.record_event"):
        yield env_file


def test_snapshot_diff_no_diff(mock_deps):
    result = snapshot_diff("myapp", "pass", str(mock_deps))
    from envault.diff import has_diff
    assert not has_diff(result)


def test_snapshot_diff_detects_changed(mock_deps):
    mock_deps.write_text(LOCAL_ENV_CHANGED)
    result = snapshot_diff("myapp", "pass", str(mock_deps))
    assert any(r["key"] == "KEY_B" and r["status"] == "changed" for r in result)


def test_snapshot_diff_detects_added(mock_deps):
    mock_deps.write_text(LOCAL_ENV_ADDED)
    result = snapshot_diff("myapp", "pass", str(mock_deps))
    assert any(r["key"] == "KEY_C" and r["status"] == "added" for r in result)


def test_snapshot_diff_raises_if_file_missing():
    with patch("envault.env_diff_watch.get_env_vars", return_value=VAULT_ENV):
        with pytest.raises(DiffWatchError, match="File not found"):
            snapshot_diff("myapp", "pass", "/no/such/file.env")


def test_snapshot_diff_raises_if_vault_missing(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(LOCAL_ENV_SAME)
    with patch("envault.env_diff_watch.get_env_vars", side_effect=Exception("not found")):
        with pytest.raises(DiffWatchError, match="Could not load vault"):
            snapshot_diff("ghost", "pass", str(env_file))


def test_watch_diff_calls_on_diff_when_file_changes(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(LOCAL_ENV_SAME)

    call_count = {"n": 0}

    def fake_sleep(interval):
        call_count["n"] += 1
        if call_count["n"] == 1:
            env_file.write_text(LOCAL_ENV_CHANGED)

    collected = []

    with patch("envault.env_diff_watch.get_env_vars", return_value=VAULT_ENV), \
         patch("envault.env_diff_watch.record_event"), \
         patch("envault.env_diff_watch.time.sleep", side_effect=fake_sleep):
        watch_diff(
            "myapp", "pass", str(env_file),
            interval=0.01,
            max_iterations=2,
            on_diff=lambda r: collected.append(r),
        )

    assert len(collected) == 1


def test_watch_diff_no_callback_on_no_change(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(LOCAL_ENV_SAME)
    collected = []

    with patch("envault.env_diff_watch.get_env_vars", return_value=VAULT_ENV), \
         patch("envault.env_diff_watch.record_event"), \
         patch("envault.env_diff_watch.time.sleep"):
        watch_diff(
            "myapp", "pass", str(env_file),
            interval=0.01,
            max_iterations=3,
            on_diff=lambda r: collected.append(r),
        )

    assert len(collected) == 0
