"""CLI commands for env_tokenize feature."""

from envault.env_tokenize import (
    TokenizeError,
    tokenize_vault,
    get_token_roots,
    group_by_root,
    format_tokenize_result,
)


def cmd_tokenize(
    vault_name: str,
    password: str,
    delimiter: str = "_",
    prefix_filter: str | None = None,
    group: bool = False,
    raw: bool = False,
) -> dict:
    """Tokenize vault keys and return structured result."""
    try:
        tokenized = tokenize_vault(
            vault_name, password, delimiter=delimiter, prefix_filter=prefix_filter
        )
    except TokenizeError as e:
        return {"ok": False, "error": str(e)}

    roots = get_token_roots(tokenized)
    grouped = group_by_root(tokenized) if group else {}

    result: dict = {
        "ok": True,
        "vault": vault_name,
        "total": len(tokenized),
        "roots": roots,
        "tokenized": tokenized,
    }

    if group:
        result["grouped"] = grouped

    if not raw:
        result["formatted"] = format_tokenize_result(tokenized)

    return result
