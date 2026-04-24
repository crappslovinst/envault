"""CLI command for vault summarization."""

from envault.env_summarize import SummarizeError, summarize_vault, format_summary


def cmd_summarize(vault_name: str, password: str, raw: bool = False) -> dict:
    """Summarize a vault and return the result dict.

    Adds a 'formatted' key unless *raw* is True.
    Raises SummarizeError on failure.
    """
    result = summarize_vault(vault_name, password)
    if not raw:
        result["formatted"] = format_summary(result)
    return result
