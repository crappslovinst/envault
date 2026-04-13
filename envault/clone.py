"""Clone a vault under a new name, optionally with a new password."""

from envault.vault_ops import get_env_vars, push_env
from envault.storage import vault_exists
from envault.audit import record_event


class CloneError(Exception):
    pass


def clone_vault(
    src_name: str,
    dst_name: str,
    src_password: str,
    dst_password: str | None = None,
) -> dict:
    """Clone *src_name* vault into a new vault called *dst_name*.

    Parameters
    ----------
    src_name:     name of the existing vault to clone from
    dst_name:     name of the new vault to create
    src_password: password for the source vault
    dst_password: password for the destination vault; defaults to src_password

    Returns a summary dict with keys: source, destination, keys_copied.
    """
    if not vault_exists(src_name):
        raise CloneError(f"Source vault '{src_name}' does not exist.")

    if vault_exists(dst_name):
        raise CloneError(
            f"Destination vault '{dst_name}' already exists. "
            "Delete it first or choose a different name."
        )

    if dst_password is None:
        dst_password = src_password

    env_vars = get_env_vars(src_name, src_password)

    push_env(dst_name, dst_password, env_vars)

    record_event(
        vault=dst_name,
        action="clone",
        detail=f"cloned from '{src_name}'",
    )

    return {
        "source": src_name,
        "destination": dst_name,
        "keys_copied": len(env_vars),
    }
