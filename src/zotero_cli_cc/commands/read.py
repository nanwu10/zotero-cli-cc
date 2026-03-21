from __future__ import annotations

import click

from zotero_cli_cc.config import load_config, get_data_dir
from zotero_cli_cc.core.reader import ZoteroReader
from zotero_cli_cc.formatter import format_item_detail, format_error


@click.command("read")
@click.argument("key")
@click.pass_context
def read_cmd(ctx: click.Context, key: str) -> None:
    """View item details."""
    cfg = load_config()
    data_dir = get_data_dir(cfg)
    db_path = data_dir / "zotero.sqlite"
    reader = ZoteroReader(db_path)
    json_out = ctx.obj.get("json", False)
    try:
        item = reader.get_item(key)
        if item is None:
            click.echo(format_error(f"Item '{key}' not found", output_json=json_out))
            return
        notes = reader.get_notes(key)
        detail = ctx.obj.get("detail", "standard")
        click.echo(format_item_detail(item, notes, output_json=json_out, detail=detail))
    finally:
        reader.close()
