from __future__ import annotations

import os

import click

from zotero_cli_cc.config import load_config, get_data_dir
from zotero_cli_cc.core.reader import ZoteroReader
from zotero_cli_cc.core.writer import ZoteroWriter, SYNC_REMINDER
from zotero_cli_cc.formatter import format_notes, format_error
from zotero_cli_cc.models import ErrorInfo


@click.command("note")
@click.argument("key")
@click.option("--add", "content", default=None, help="Add a new note")
@click.pass_context
def note_cmd(ctx: click.Context, key: str, content: str | None) -> None:
    """View or add notes for an item."""
    cfg = load_config(profile=ctx.obj.get("profile"))
    json_out = ctx.obj.get("json", False)

    if content:
        # Write mode
        library_id = os.environ.get("ZOT_LIBRARY_ID", cfg.library_id)
        api_key = os.environ.get("ZOT_API_KEY", cfg.api_key)
        if not library_id or not api_key:
            click.echo(format_error(ErrorInfo(message="Write credentials not configured", context="note", hint="Run 'zot config init' to set up API credentials"), output_json=json_out))
            return
        writer = ZoteroWriter(library_id=library_id, api_key=api_key)
        note_key = writer.add_note(key, content)
        click.echo(f"Note added: {note_key}")
        click.echo(SYNC_REMINDER)
    else:
        # Read mode
        data_dir = get_data_dir(cfg)
        db_path = data_dir / "zotero.sqlite"
        reader = ZoteroReader(db_path)
        try:
            notes = reader.get_notes(key)
            if not notes:
                click.echo(format_error(ErrorInfo(message=f"No notes found for '{key}'", context="note", hint="Add one with: zot note KEY --add 'content'"), output_json=json_out))
                return
            click.echo(format_notes(notes, output_json=json_out))
        finally:
            reader.close()
