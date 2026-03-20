from __future__ import annotations

import click

from zotero_cli_cc.config import load_config, get_data_dir
from zotero_cli_cc.core.reader import ZoteroReader
from zotero_cli_cc.formatter import format_items


@click.command("list")
@click.option("--collection", default=None, help="Filter by collection name")
@click.pass_context
def list_cmd(ctx: click.Context, collection: str | None) -> None:
    """List items in the Zotero library."""
    cfg = load_config()
    data_dir = get_data_dir(cfg)
    db_path = data_dir / "zotero.sqlite"
    reader = ZoteroReader(db_path)
    try:
        limit = ctx.obj.get("limit", cfg.default_limit)
        result = reader.search("", collection=collection, limit=limit)
        click.echo(format_items(result.items, output_json=ctx.obj.get("json", False)))
    finally:
        reader.close()
