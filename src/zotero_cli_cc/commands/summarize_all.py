"""Batch export all item summaries for AI consumption."""
from __future__ import annotations

import json

import click

from zotero_cli_cc.config import load_config, get_data_dir
from zotero_cli_cc.core.reader import ZoteroReader


@click.command("summarize-all")
@click.pass_context
def summarize_all_cmd(ctx: click.Context) -> None:
    """Export all items with key, title, and abstract for AI classification."""
    cfg = load_config(profile=ctx.obj.get("profile"))
    data_dir = get_data_dir(cfg)
    db_path = data_dir / "zotero.sqlite"
    limit = ctx.obj.get("limit", 10000)
    reader = ZoteroReader(db_path)
    try:
        result = reader.search("", limit=limit)
        items = []
        for item in result.items:
            items.append({
                "key": item.key,
                "title": item.title,
                "authors": [c.full_name for c in item.creators],
                "abstract": item.abstract,
                "tags": item.tags,
                "date": item.date,
            })
        click.echo(json.dumps(items, indent=2, ensure_ascii=False))
    finally:
        reader.close()
