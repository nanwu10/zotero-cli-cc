from __future__ import annotations

import click

from zotero_cli_cc.config import get_data_dir, load_config
from zotero_cli_cc.core.reader import ZoteroReader
from zotero_cli_cc.formatter import format_items


@click.command("search")
@click.argument("query")
@click.option("--collection", default=None, help="Filter by collection name")
@click.pass_context
def search_cmd(ctx: click.Context, query: str, collection: str | None) -> None:
    """Search the Zotero library by title, author, tag, or full text.

    \b
    Examples:
      zot search "transformer attention"
      zot search "BERT" --collection "NLP"
      zot --json search "single cell"
      zot --detail minimal search "GAN"
    """
    cfg = load_config(profile=ctx.obj.get("profile"))
    data_dir = get_data_dir(cfg)
    db_path = data_dir / "zotero.sqlite"
    reader = ZoteroReader(db_path)
    try:
        limit = ctx.obj.get("limit", cfg.default_limit)
        result = reader.search(query, collection=collection, limit=limit)
        if not result.items:
            if ctx.obj.get("json"):
                click.echo("[]")
            else:
                click.echo("No results found.")
            return
        detail = ctx.obj.get("detail", "standard")
        click.echo(format_items(result.items, output_json=ctx.obj.get("json", False), detail=detail))
    finally:
        reader.close()
