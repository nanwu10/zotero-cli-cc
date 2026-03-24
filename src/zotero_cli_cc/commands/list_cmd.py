from __future__ import annotations

import click

from zotero_cli_cc.config import get_data_dir, load_config
from zotero_cli_cc.core.reader import ZoteroReader
from zotero_cli_cc.formatter import format_items


@click.command("list")
@click.option("--collection", default=None, help="Filter by collection name")
@click.option("--type", "item_type", default=None, help="Filter by item type (e.g. journalArticle, book, preprint)")
@click.pass_context
def list_cmd(ctx: click.Context, collection: str | None, item_type: str | None) -> None:
    """List items in the Zotero library.

    \b
    Examples:
      zot list
      zot list --collection "Machine Learning"
      zot --limit 10 list
      zot --json list --collection "NLP"
    """
    cfg = load_config(profile=ctx.obj.get("profile"))
    data_dir = get_data_dir(cfg)
    db_path = data_dir / "zotero.sqlite"
    reader = ZoteroReader(db_path)
    try:
        limit = ctx.obj.get("limit", cfg.default_limit)
        result = reader.search("", collection=collection, item_type=item_type, limit=limit)
        detail = ctx.obj.get("detail", "standard")
        click.echo(format_items(result.items, output_json=ctx.obj.get("json", False), detail=detail))
    finally:
        reader.close()
