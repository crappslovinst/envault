"""Main CLI entry point for envault."""

import argparse
import sys

from envault.cli_ops import cmd_push, cmd_pull, cmd_list, cmd_show
from envault.cli_audit import cmd_log, cmd_clear_log
from envault.cli_export import cmd_export
from envault.cli_import import cmd_import
from envault.cli_snapshot import cmd_snapshot_create, cmd_snapshot_list, cmd_snapshot_restore, cmd_snapshot_delete
from envault.cli_clone import cmd_clone
from envault.cli_share import cmd_share_export, cmd_share_import
from envault.cli_compare import cmd_compare
from envault.cli_rename import cmd_rename
from envault.cli_ttl import cmd_set_ttl, cmd_get_ttl, cmd_clear_ttl, cmd_check_expired
from envault.cli_alias import cmd_set_alias, cmd_remove_alias, cmd_list_aliases, cmd_resolve_alias
from envault.cli_lint import cmd_lint
from envault.cli_schema import cmd_validate_schema
from envault.cli_health import cmd_health, cmd_health_summary
from envault.cli_stats import cmd_stats
from envault.cli_count import cmd_count
from envault.cli_filter import cmd_filter
from envault.cli_grep import cmd_grep
from envault.cli_set import cmd_set, cmd_delete, cmd_set_many
from envault.cli_sort import cmd_sort
from envault.cli_fmt import cmd_fmt
from envault.cli_quota import cmd_quota
from envault.cli_secrets import cmd_scan_secrets
from envault.cli_redact import cmd_redact
from envault.cli_mask import cmd_mask
from envault.cli_status import cmd_status
from envault.cli_archive import cmd_archive, cmd_unarchive, cmd_list_archived
from envault.cli_cascade import cmd_cascade
from envault.cli_resolve import cmd_resolve, cmd_find_refs
from envault.cli_diff_watch import cmd_snapshot_diff, cmd_watch_diff
from envault.cli_group import cmd_group_add, cmd_group_remove, cmd_group_list, cmd_group_members, cmd_group_delete
from envault.cli_permissions import cmd_set_permission, cmd_remove_permission, cmd_get_permission, cmd_list_permissions
from envault.cli_remind import cmd_set_reminder, cmd_check_reminders, cmd_list_reminders, cmd_clear_reminder
from envault.cli_webhook import cmd_set_webhook, cmd_remove_webhook, cmd_list_webhooks
from envault.cli_merge_policy import cmd_set_policy, cmd_get_policy, cmd_clear_policy
from envault.cli_notes import cmd_add_note, cmd_list_notes, cmd_delete_note, cmd_clear_notes
from envault.cli_default import cmd_set_defaults
from envault.cli_env_copy import cmd_copy_keys, cmd_copy_all
from envault.cli_env_diff_report import cmd_diff_report


def _print_result(result: dict) -> None:
    """Print a command result dict. Uses 'formatted' if present, else pretty-prints."""
    if "formatted" in result:
        print(result["formatted"])
    elif "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
    else:
        import json
        print(json.dumps(result, indent=2, default=str))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envault",
        description="Securely manage and sync .env files using encrypted local storage.",
    )
    sub = parser.add_subparsers(dest="command", metavar="<command>")

    # push
    p = sub.add_parser("push", help="Encrypt and store a .env file")
    p.add_argument("vault", help="Vault name")
    p.add_argument("password", help="Encryption password")
    p.add_argument("--file", default=".env", help="Path to .env file (default: .env)")

    # pull
    p = sub.add_parser("pull", help="Decrypt and write a .env file")
    p.add_argument("vault")
    p.add_argument("password")
    p.add_argument("--file", default=".env")

    # list
    sub.add_parser("list", help="List all vaults")

    # show
    p = sub.add_parser("show", help="Show decrypted contents of a vault")
    p.add_argument("vault")
    p.add_argument("password")

    # set
    p = sub.add_parser("set", help="Set a key in a vault")
    p.add_argument("vault")
    p.add_argument("password")
    p.add_argument("key")
    p.add_argument("value")

    # delete
    p = sub.add_parser("delete", help="Delete a key from a vault")
    p.add_argument("vault")
    p.add_argument("password")
    p.add_argument("key")

    # lint
    p = sub.add_parser("lint", help="Lint a vault for common issues")
    p.add_argument("vault")
    p.add_argument("password")

    # stats
    p = sub.add_parser("stats", help="Show stats for a vault")
    p.add_argument("vault")
    p.add_argument("password")

    # health
    p = sub.add_parser("health", help="Check health of a vault")
    p.add_argument("vault")
    p.add_argument("password")
    p.add_argument("--required-keys", nargs="*", default=None)

    # status
    p = sub.add_parser("status", help="Show vault status")
    p.add_argument("vault")
    p.add_argument("password")

    # log
    p = sub.add_parser("log", help="Show audit log")
    p.add_argument("--vault", default=None)
    p.add_argument("--limit", type=int, default=20)

    # export
    p = sub.add_parser("export", help="Export vault to a file")
    p.add_argument("vault")
    p.add_argument("password")
    p.add_argument("--format", default="dotenv", choices=["dotenv", "shell", "json"])
    p.add_argument("--output", default=None)
    p.add_argument("--prefix", default="")

    # scan-secrets
    p = sub.add_parser("scan-secrets", help="Scan vault for sensitive keys")
    p.add_argument("vault")
    p.add_argument("password")

    # quota
    p = sub.add_parser("quota", help="Check vault quota")
    p.add_argument("vault")
    p.add_argument("password")
    p.add_argument("--max-keys", type=int, default=100)
    p.add_argument("--max-value-length", type=int, default=1000)

    return parser


def main(argv=None) -> None:
    """Entry point for the envault CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        sys.exit(0)

    try:
        if args.command == "push":
            result = cmd_push(args.vault, args.password, env_file=args.file)
        elif args.command == "pull":
            result = cmd_pull(args.vault, args.password, output_file=args.file)
        elif args.command == "list":
            result = cmd_list()
        elif args.command == "show":
            result = cmd_show(args.vault, args.password)
        elif args.command == "set":
            result = cmd_set(args.vault, args.password, args.key, args.value)
        elif args.command == "delete":
            result = cmd_delete(args.vault, args.password, args.key)
        elif args.command == "lint":
            result = cmd_lint(args.vault, args.password)
        elif args.command == "stats":
            result = cmd_stats(args.vault, args.password)
        elif args.command == "health":
            result = cmd_health(args.vault, args.password, required_keys=args.required_keys)
        elif args.command == "status":
            result = cmd_status(args.vault, args.password)
        elif args.command == "log":
            result = cmd_log(vault=args.vault, limit=args.limit)
        elif args.command == "export":
            result = cmd_export(
                args.vault, args.password,
                fmt=args.format, output=args.output, prefix=args.prefix
            )
        elif args.command == "scan-secrets":
            result = cmd_scan_secrets(args.vault, args.password)
        elif args.command == "quota":
            result = cmd_quota(
                args.vault, args.password,
                max_keys=args.max_keys, max_value_length=args.max_value_length
            )
        else:
            parser.print_help()
            sys.exit(1)

        _print_result(result)

        if result.get("ok") is False or "error" in result:
            sys.exit(1)

    except KeyboardInterrupt:
        print("\nAborted.", file=sys.stderr)
        sys.exit(130)
    except Exception as exc:  # noqa: BLE001
        print(f"Fatal: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
