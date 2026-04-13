"""CLI commands for vault sharing."""

from envault.share import (
    export_bundle,
    import_bundle,
    save_bundle_to_file,
    load_bundle_from_file,
    ShareError,
)


def cmd_share_export(
    vault_name: str,
    password: str,
    bundle_password: str,
    output_file: str | None = None,
) -> dict:
    """
    Export a vault as an encrypted bundle.
    Returns a dict with the bundle string and optional saved path.
    """
    bundle = export_bundle(vault_name, password, bundle_password)

    result = {"vault": vault_name, "bundle": bundle, "saved_to": None}

    if output_file:
        save_bundle_to_file(bundle, output_file)
        result["saved_to"] = output_file

    return result


def cmd_share_import(
    bundle_or_file: str,
    bundle_password: str,
    new_password: str,
    vault_name: str | None = None,
    from_file: bool = False,
) -> dict:
    """
    Import a vault from an encrypted bundle string or file.
    Returns a summary dict.
    """
    if from_file:
        bundle = load_bundle_from_file(bundle_or_file)
    else:
        bundle = bundle_or_file

    return import_bundle(bundle, bundle_password, new_password, vault_name)
