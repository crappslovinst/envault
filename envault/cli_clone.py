"""CLI command handler for the clone feature."""

from envault.clone import clone_vault, CloneError


def cmd_clone(
    src_name: str,
    dst_name: str,
    src_password: str,
    dst_password: str | None = None,
) -> str:
    """Clone a vault and return a human-readable result string.

    Raises CloneError on failure (callers may catch and display).
    """
    summary = clone_vault(
        src_name=src_name,
        dst_name=dst_name,
        src_password=src_password,
        dst_password=dst_password,
    )

    same_pw = dst_password is None or dst_password == src_password
    pw_note = " (same password)" if same_pw else " (new password set)"

    return (
        f"Cloned '{summary['source']}' → '{summary['destination']}'{pw_note}. "
        f"{summary['keys_copied']} key(s) copied."
    )
