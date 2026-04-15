"""CLI commands for generating env diff reports."""

from envault.env_diff_report import generate_report, save_report, ReportError


def cmd_diff_report(
    vault_name: str,
    password: str,
    env_file: str,
    output_file: str = None,
    show_unchanged: bool = False,
) -> dict:
    """
    Generate a diff report between a vault and a local .env file.
    Optionally save to output_file.
    Returns a summary dict.
    """
    report = generate_report(vault_name, password, env_file)

    if output_file:
        save_report(report, output_file)

    summary_lines = []
    for entry in report["formatted"]:
        if not show_unchanged and entry.startswith(" "):
            continue
        summary_lines.append(entry)

    return {
        "vault": vault_name,
        "env_file": env_file,
        "has_diff": report["has_diff"],
        "added": len(report["added"]),
        "removed": len(report["removed"]),
        "changed": len(report["changed"]),
        "unchanged": len(report["unchanged"]),
        "output_file": output_file,
        "lines": summary_lines,
    }


def format_report_summary(result: dict) -> str:
    """Format cmd_diff_report result into a printable string."""
    lines = [
        f"Vault   : {result['vault']}",
        f"File    : {result['env_file']}",
        f"Added   : {result['added']}",
        f"Removed : {result['removed']}",
        f"Changed : {result['changed']}",
        f"Unchanged: {result['unchanged']}",
    ]
    if result["output_file"]:
        lines.append(f"Saved to: {result['output_file']}")
    if result["lines"]:
        lines.append("")
        lines.extend(result["lines"])
    return "\n".join(lines)
