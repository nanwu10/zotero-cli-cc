from __future__ import annotations

import os

import click

from zotero_cli_cc.config import load_config, get_data_dir
from zotero_cli_cc.core.reader import ZoteroReader
from zotero_cli_cc.core.writer import ZoteroWriter, SYNC_REMINDER
from zotero_cli_cc.formatter import format_collections, format_items, format_error
from zotero_cli_cc.models import ErrorInfo


@click.group("collection")
def collection_group() -> None:
    """Manage Zotero collections."""
    pass


@collection_group.command("list")
@click.pass_context
def collection_list(ctx: click.Context) -> None:
    """List all collections."""
    cfg = load_config(profile=ctx.obj.get("profile"))
    data_dir = get_data_dir(cfg)
    db_path = data_dir / "zotero.sqlite"
    reader = ZoteroReader(db_path)
    try:
        collections = reader.get_collections()
        click.echo(format_collections(collections, output_json=ctx.obj.get("json", False)))
    finally:
        reader.close()


@collection_group.command("items")
@click.argument("key")
@click.pass_context
def collection_items(ctx: click.Context, key: str) -> None:
    """List items in a collection."""
    cfg = load_config(profile=ctx.obj.get("profile"))
    data_dir = get_data_dir(cfg)
    db_path = data_dir / "zotero.sqlite"
    reader = ZoteroReader(db_path)
    try:
        items = reader.get_collection_items(key)
        click.echo(format_items(items, output_json=ctx.obj.get("json", False)))
    finally:
        reader.close()


@collection_group.command("create")
@click.argument("name")
@click.option("--parent", default=None, help="Parent collection key")
@click.pass_context
def collection_create(ctx: click.Context, name: str, parent: str | None) -> None:
    """Create a new collection."""
    cfg = load_config(profile=ctx.obj.get("profile"))
    json_out = ctx.obj.get("json", False)
    library_id = os.environ.get("ZOT_LIBRARY_ID", cfg.library_id)
    api_key = os.environ.get("ZOT_API_KEY", cfg.api_key)
    if not library_id or not api_key:
        click.echo(format_error(ErrorInfo(message="Write credentials not configured", context="collection", hint="Run 'zot config init' to set up API credentials"), output_json=json_out))
        return
    writer = ZoteroWriter(library_id=library_id, api_key=api_key)
    key = writer.create_collection(name, parent_key=parent)
    click.echo(f"Collection created: {key}")
    click.echo(SYNC_REMINDER)


@collection_group.command("move")
@click.argument("item_key")
@click.argument("collection_key")
@click.pass_context
def collection_move(ctx: click.Context, item_key: str, collection_key: str) -> None:
    """Move an item to a collection."""
    cfg = load_config(profile=ctx.obj.get("profile"))
    json_out = ctx.obj.get("json", False)
    library_id = os.environ.get("ZOT_LIBRARY_ID", cfg.library_id)
    api_key = os.environ.get("ZOT_API_KEY", cfg.api_key)
    if not library_id or not api_key:
        click.echo(format_error(ErrorInfo(message="Write credentials not configured", context="collection", hint="Run 'zot config init' to set up API credentials"), output_json=json_out))
        return
    writer = ZoteroWriter(library_id=library_id, api_key=api_key)
    try:
        writer.move_to_collection(item_key, collection_key)
        click.echo(f"Item {item_key} moved to collection {collection_key}")
        click.echo(SYNC_REMINDER)
    except Exception as e:
        click.echo(format_error(ErrorInfo(message=str(e), context="collection move", hint="Check item and collection keys"), output_json=json_out))


@collection_group.command("delete")
@click.argument("key")
@click.pass_context
def collection_delete(ctx: click.Context, key: str) -> None:
    """Delete a collection."""
    cfg = load_config(profile=ctx.obj.get("profile"))
    json_out = ctx.obj.get("json", False)
    library_id = os.environ.get("ZOT_LIBRARY_ID", cfg.library_id)
    api_key = os.environ.get("ZOT_API_KEY", cfg.api_key)
    if not library_id or not api_key:
        click.echo(format_error(ErrorInfo(message="Write credentials not configured", context="collection", hint="Run 'zot config init' to set up API credentials"), output_json=json_out))
        return
    writer = ZoteroWriter(library_id=library_id, api_key=api_key)
    try:
        writer.delete_collection(key)
        click.echo(f"Collection {key} deleted")
        click.echo(SYNC_REMINDER)
    except Exception as e:
        click.echo(format_error(ErrorInfo(message=str(e), context="collection delete", hint="Check collection key"), output_json=json_out))


@collection_group.command("rename")
@click.argument("key")
@click.argument("new_name")
@click.pass_context
def collection_rename(ctx: click.Context, key: str, new_name: str) -> None:
    """Rename a collection."""
    cfg = load_config(profile=ctx.obj.get("profile"))
    json_out = ctx.obj.get("json", False)
    library_id = os.environ.get("ZOT_LIBRARY_ID", cfg.library_id)
    api_key = os.environ.get("ZOT_API_KEY", cfg.api_key)
    if not library_id or not api_key:
        click.echo(format_error(ErrorInfo(message="Write credentials not configured", context="collection", hint="Run 'zot config init' to set up API credentials"), output_json=json_out))
        return
    writer = ZoteroWriter(library_id=library_id, api_key=api_key)
    try:
        writer.rename_collection(key, new_name)
        click.echo(f"Collection {key} renamed to '{new_name}'")
        click.echo(SYNC_REMINDER)
    except Exception as e:
        click.echo(format_error(ErrorInfo(message=str(e), context="collection rename", hint="Check collection key"), output_json=json_out))
