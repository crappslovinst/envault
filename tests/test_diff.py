import pytest
from envault.diff import diff_envs, has_diff, format_diff


LOCAL = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "SECRET": "old_secret",
    "ONLY_LOCAL": "yes",
}

REMOTE = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "SECRET": "new_secret",
    "ONLY_REMOTE": "true",
}


def test_diff_added():
    result = diff_envs(LOCAL, REMOTE)
    assert result["added"] == {"ONLY_REMOTE": "true"}


def test_diff_removed():
    result = diff_envs(LOCAL, REMOTE)
    assert result["removed"] == {"ONLY_LOCAL": "yes"}


def test_diff_changed():
    result = diff_envs(LOCAL, REMOTE)
    assert result["changed"] == {
        "SECRET": {"local": "old_secret", "remote": "new_secret"}
    }


def test_diff_unchanged():
    result = diff_envs(LOCAL, REMOTE)
    assert result["unchanged"] == {"DB_HOST": "localhost", "DB_PORT": "5432"}


def test_has_diff_true():
    result = diff_envs(LOCAL, REMOTE)
    assert has_diff(result) is True


def test_has_diff_false_when_identical():
    result = diff_envs(LOCAL, LOCAL)
    assert has_diff(result) is False


def test_diff_identical_envs():
    result = diff_envs(LOCAL, LOCAL)
    assert result["added"] == {}
    assert result["removed"] == {}
    assert result["changed"] == {}
    assert result["unchanged"] == LOCAL


def test_format_diff_contains_markers():
    result = diff_envs(LOCAL, REMOTE)
    output = format_diff(result)
    assert "+ ONLY_REMOTE" in output
    assert "- ONLY_LOCAL" in output
    assert "~ SECRET" in output


def test_format_diff_no_diff():
    result = diff_envs(LOCAL, LOCAL)
    output = format_diff(result)
    assert "(no differences)" in output


def test_diff_empty_dicts():
    result = diff_envs({}, {})
    assert not has_diff(result)
    assert result["unchanged"] == {}
