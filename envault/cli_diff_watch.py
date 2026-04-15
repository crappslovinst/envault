"""CLI commands for live diff watching and one-shot snapshot diffs."""

from envault.env_diff_watch import snapshot_diff, watch_diff, DiffWatchError
from envault.diff import format_diff, has_diff


def cmd_snapshot_diff(vault_name: str, password: str, env_file: str) -> dict:
    """Return a formatted one-shot diff between vault and local .env file."""
    try:
        result = snapshot_diff(vault_name, password, env_file)
    except DiffWatchError as e:
        return {"ok": False, "error": str(e)}

    return {
        "ok": True,
        "vault": vault_name,
        "file": env_file,
        "has_diff": has_diff(result),
        "diff": result,
        "formatted": format_diff(result),
    }


def cmd_watch_diff(
    vault_name: str,
    password: str,
    env_file: str,
    interval: float = 2.0,
    max_iterations: int = None,
    quiet: bool = False,
) -> dict:
    """Start watching a .env file and print diffs as they occur."""
    changes_detected = []

    def _on_diff(result: dict) -> None:
        changes_detected.append(result)
        if not quiet:
            print(format_diff(result))

    try:
        watch_diff(
            vault_name=vault_name,
            password=password,
            env_file=env_file,
            interval=interval,
            max_iterations=max_iterations,
            on_diff=_on_diff,
        )
    except DiffWatchError as e:
        return {"ok": False, "error": str(e)}

    return {
        "ok": True,
        "vault": vault_name,
        "file": env_file,
        "changes_detected": len(changes_detected),
    }
