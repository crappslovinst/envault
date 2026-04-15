"""CLI commands for env linting."""

from envault.env_lint import lint_vault, format_lint_result, LintError, LINT_RULES


def cmd_lint(vault_name: str, password: str, rules: list = None, quiet: bool = False) -> dict:
    """
    Run lint on a vault and return a result dict.

    Args:
        vault_name: Name of the vault to lint.
        password: Vault password.
        rules: Optional list of rule names to run (defaults to all).
        quiet: If True, suppress formatted output in the result.

    Returns:
        dict with keys: vault, total_issues, passed, findings, formatted (unless quiet).
    """
    if rules:
        unknown = [r for r in rules if r not in LINT_RULES]
        if unknown:
            return {
                "ok": False,
                "error": f"Unknown lint rules: {unknown}. Valid rules: {LINT_RULES}",
            }

    try:
        result = lint_vault(vault_name, password, rules=rules)
    except LintError as e:
        return {"ok": False, "error": str(e)}

    output = {"ok": True, **result}
    if not quiet:
        output["formatted"] = format_lint_result(result)
    return output
