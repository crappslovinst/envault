"""Split a vault into named chunks (groups of keys) for partial sync."""
from envault.vault_ops import get_env_vars, push_env

class ChunkError(Exception):
    pass

def split_vault(vault_name: str, password: str, chunks: dict[str, list[str]]) -> dict:
    """
    Split vault keys into named chunks.
    chunks = {"db": ["DB_HOST", "DB_PORT"], "app": ["APP_KEY"]}
    Returns {chunk_name: {key: value}}
    """
    env = get_env_vars(vault_name, password)
    if not env:
        raise ChunkError(f"Vault '{vault_name}' is empty or missing")

    result = {}
    for chunk_name, keys in chunks.items():
        result[chunk_name] = {k: env[k] for k in keys if k in env}

    missing = {}
    for chunk_name, keys in chunks.items():
        absent = [k for k in keys if k not in env]
        if absent:
            missing[chunk_name] = absent

    return {"chunks": result, "missing": missing}


def push_chunk(src_vault: str, src_password: str, chunk_keys: list[str],
               dst_vault: str, dst_password: str, overwrite: bool = True) -> dict:
    """Push a subset of keys from src vault into dst vault."""
    env = get_env_vars(src_vault, src_password)
    if env is None:
        raise ChunkError(f"Source vault '{src_vault}' not found")

    subset = {k: env[k] for k in chunk_keys if k in env}
    missing = [k for k in chunk_keys if k not in env]

    if not overwrite:
        try:
            existing = get_env_vars(dst_vault, dst_password) or {}
        except Exception:
            existing = {}
        subset = {k: v for k, v in subset.items() if k not in existing}

    push_env(dst_vault, dst_password, subset)

    return {
        "src": src_vault,
        "dst": dst_vault,
        "pushed": list(subset.keys()),
        "missing_in_src": missing,
    }


def format_chunk_result(result: dict) -> str:
    lines = []
    if "chunks" in result:
        for name, keys in result["chunks"].items():
            lines.append(f"[{name}] {len(keys)} key(s): {', '.join(keys) or 'none'}")
        for name, absent in result.get("missing", {}).items():
            lines.append(f"  missing in [{name}]: {', '.join(absent)}")
    else:
        lines.append(f"Pushed {len(result['pushed'])} key(s) to '{result['dst']}'")
        if result["missing_in_src"]:
            lines.append(f"  not found in src: {', '.join(result['missing_in_src'])}")
    return "\n".join(lines)
