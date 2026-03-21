from __future__ import annotations

import json

import click

from zotero_cli_cc.config import load_config, get_data_dir
from zotero_cli_cc.core.reader import ZoteroReader
from zotero_cli_cc.formatter import format_error


@click.command("summarize")
@click.argument("key")
@click.pass_context
def summarize_cmd(ctx: click.Context, key: str) -> None:
    """Output a structured summary for Claude Code consumption."""
    cfg = load_config()
    json_out = ctx.obj.get("json", False)
    data_dir = get_data_dir(cfg)
    db_path = data_dir / "zotero.sqlite"
    reader = ZoteroReader(db_path)
    try:
        item = reader.get_item(key)
        if item is None:
            click.echo(format_error(f"Item '{key}' not found", output_json=json_out))
            return
        notes = reader.get_notes(key)
        detail = ctx.obj.get("detail", "standard")
        if json_out:
            data: dict = {
                "title": item.title,
                "authors": [c.full_name for c in item.creators],
                "year": item.date,
                "doi": item.doi,
            }
            if detail != "minimal":
                data["abstract"] = item.abstract
                data["tags"] = item.tags
                data["notes"] = [n.content[:500] for n in notes]
            click.echo(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            click.echo(f"Title: {item.title}")
            click.echo(f"Authors: {', '.join(c.full_name for c in item.creators)}")
            click.echo(f"Year: {item.date or 'N/A'}")
            if item.doi:
                click.echo(f"DOI: {item.doi}")
            if detail != "minimal":
                if item.abstract:
                    click.echo(f"Key findings: {item.abstract}")
                if item.tags:
                    click.echo(f"Tags: {', '.join(item.tags)}")
                if notes:
                    click.echo(f"Notes ({len(notes)}):")
                    for n in notes:
                        click.echo(f"  {n.content[:500]}")
    finally:
        reader.close()
