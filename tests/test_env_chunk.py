import pytest
from unittest.mock import patch, MagicMock
from envault.env_chunk import split_vault, push_chunk, format_chunk_result, ChunkError

BASE_ENV = {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_KEY": "secret", "APP_ENV": "dev"}

@pytest.fixture
def mock_chunk_deps():
    with patch("envault.env_chunk.get_env_vars") as _get, \
         patch("envault.env_chunk.push_env") as _push:
        _get.return_value = BASE_ENV.copy()
        yield _get, _push


def test_split_vault_returns_chunks(mock_chunk_deps):
    _get, _ = mock_chunk_deps
    result = split_vault("myvault", "pw", {"db": ["DB_HOST", "DB_PORT"], "app": ["APP_KEY"]})
    assert result["chunks"]["db"] == {"DB_HOST": "localhost", "DB_PORT": "5432"}
    assert result["chunks"]["app"] == {"APP_KEY": "secret"}


def test_split_vault_reports_missing(mock_chunk_deps):
    result = split_vault("myvault", "pw", {"db": ["DB_HOST", "MISSING_KEY"]})
    assert "MISSING_KEY" in result["missing"]["db"]


def test_split_vault_raises_if_empty(mock_chunk_deps):
    _get, _ = mock_chunk_deps
    _get.return_value = {}
    with pytest.raises(ChunkError):
        split_vault("myvault", "pw", {"db": ["DB_HOST"]})


def test_push_chunk_pushes_subset(mock_chunk_deps):
    _get, _push = mock_chunk_deps
    result = push_chunk("src", "pw", ["DB_HOST", "DB_PORT"], "dst", "pw2")
    assert result["pushed"] == ["DB_HOST", "DB_PORT"]
    assert result["missing_in_src"] == []
    _push.assert_called_once()


def test_push_chunk_reports_missing_keys(mock_chunk_deps):
    result = push_chunk("src", "pw", ["DB_HOST", "NOPE"], "dst", "pw2")
    assert "NOPE" in result["missing_in_src"]
    assert "DB_HOST" in result["pushed"]


def test_push_chunk_no_overwrite_skips_existing(mock_chunk_deps):
    _get, _push = mock_chunk_deps
    _get.side_effect = [BASE_ENV.copy(), {"DB_HOST": "other"}]
    result = push_chunk("src", "pw", ["DB_HOST", "DB_PORT"], "dst", "pw2", overwrite=False)
    assert "DB_HOST" not in result["pushed"]
    assert "DB_PORT" in result["pushed"]


def test_push_chunk_raises_if_src_missing(mock_chunk_deps):
    _get, _ = mock_chunk_deps
    _get.return_value = None
    with pytest.raises(ChunkError):
        push_chunk("missing", "pw", ["DB_HOST"], "dst", "pw2")


def test_format_chunk_result_split():
    result = {"chunks": {"db": {"DB_HOST": "localhost"}}, "missing": {}}
    out = format_chunk_result(result)
    assert "db" in out
    assert "DB_HOST" in out


def test_format_chunk_result_push():
    result = {"src": "a", "dst": "b", "pushed": ["KEY1"], "missing_in_src": []}
    out = format_chunk_result(result)
    assert "KEY1" in out
    assert "b" in out
