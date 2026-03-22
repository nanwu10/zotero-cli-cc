from __future__ import annotations

import os

import click

from zotero_cli_cc.config import load_config
from zotero_cli_cc.core.writer import ZoteroWriter, ZoteroWriteError, SYNC_REMINDER
from zotero_cli_cc.formatter import format_error
from zotero_cli_cc.models import ErrorInfo


@click.command("delete")
@click.argument("key")
@click.option("--yes", is_flag=True, help="Skip confirmation")
@click.option("--dry-run", is_flag=True, help="Show what would be deleted without executing")
@click.pass_context
def delete_cmd(ctx: click.Context, key: str, yes: bool, dry_run: bool) -> None:
    """Delete an item (move to trash)."""
    cfg = load_config(profile=ctx.obj.get("profile"))
    json_out = ctx.obj.get("json", False)
    if dry_run:
        click.echo(f"[dry-run] Would delete item '{key}' (move to trash)")
        return
    library_id = os.environ.get("ZOT_LIBRARY_ID", cfg.library_id)
    api_key = os.environ.get("ZOT_API_KEY", cfg.api_key)
    if not library_id or not api_key:
        click.echo(format_error(ErrorInfo(message="Write credentials not configured", context="delete", hint="Run 'zot config init' to set up API credentials"), output_json=json_out))
        return
    no_interaction = ctx.obj.get("no_interaction", False)
    if not yes and not no_interaction:
        if not click.confirm(f"Delete item '{key}'?"):
            click.echo("Cancelled.")
            return
    writer = ZoteroWriter(library_id=library_id, api_key=api_key)
    try:
        writer.delete_item(key)
        click.echo(f"Item '{key}' moved to trash.")
        click.echo(SYNC_REMINDER)
    except ZoteroWriteError as e:
        click.echo(format_error(ErrorInfo(message=str(e), context="delete", hint="Check item key and API credentials"), output_json=json_out))
