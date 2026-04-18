"""CLI commands for vault chunking."""
from envault.env_chunk import split_vault, push_chunk, format_chunk_result, ChunkError


def cmd_split(vault: str, password: str, chunks: dict[str, list[str]],
              raw: bool = False) -> dict:
    """
    Split a vault into named chunks.
    chunks = {"db": ["DB_HOST"], "app": ["APP_KEY"]}
    """
    try:
        result = split_vault(vault, password, chunks)
    except ChunkError as e:
        return {"ok": False, "error": str(e)}
    if not raw:
        result["formatted"] = format_chunk_result(result)
    return {"ok": True, **result}


def cmd_push_chunk(src: str, src_password: str, keys: list[str],
                   dst: str, dst_password: str,
                   overwrite: bool = True, raw: bool = False) -> dict:
    """Push a subset of keys from one vault to another."""
    try:
        result = push_chunk(src, src_password, keys, dst, dst_password, overwrite)
    except ChunkError as e:
        return {"ok": False, "error": str(e)}
    if not raw:
        result["formatted"] = format_chunk_result(result)
    return {"ok": True, **result}
