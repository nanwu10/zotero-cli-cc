"""MCP server exposing read-only Zotero tools via FastMCP."""
from __future__ import annotations

from pathlib import Path

from mcp.server.fastmcp import FastMCP

from zotero_cli_cc.config import get_data_dir, load_config
from zotero_cli_cc.core.pdf_extractor import extract_text_from_pdf
from zotero_cli_cc.core.reader import ZoteroReader
from zotero_cli_cc.models import Collection, Item, Note

mcp = FastMCP("zotero", instructions="Read-only access to a local Zotero library")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_reader() -> ZoteroReader:
    """Create a ZoteroReader from the user's config."""
    cfg = load_config()
    data_dir = get_data_dir(cfg)
    db_path = data_dir / "zotero.sqlite"
    return ZoteroReader(db_path)


def _item_to_dict(item: Item) -> dict:
    return {
        "key": item.key,
        "item_type": item.item_type,
        "title": item.title,
        "creators": [{"name": c.full_name, "type": c.creator_type} for c in item.creators],
        "abstract": item.abstract,
        "date": item.date,
        "url": item.url,
        "doi": item.doi,
        "tags": item.tags,
        "collections": item.collections,
        "date_added": item.date_added,
        "date_modified": item.date_modified,
    }


def _note_to_dict(note: Note) -> dict:
    return {
        "key": note.key,
        "parent_key": note.parent_key,
        "content": note.content,
        "tags": note.tags,
    }


def _collection_to_dict(coll: Collection) -> dict:
    return {
        "key": coll.key,
        "name": coll.name,
        "parent_key": coll.parent_key,
        "children": [_collection_to_dict(c) for c in coll.children],
    }


# ---------------------------------------------------------------------------
# Handler functions (testable without MCP decorator)
# ---------------------------------------------------------------------------


def _handle_search(query: str, collection: str | None, limit: int) -> dict:
    reader = _get_reader()
    try:
        result = reader.search(query, collection=collection, limit=limit)
        return {
            "items": [_item_to_dict(i) for i in result.items],
            "total": result.total,
            "query": result.query,
        }
    finally:
        reader.close()


def _handle_list_items(limit: int) -> dict:
    reader = _get_reader()
    try:
        result = reader.search("", collection=None, limit=limit)
        return {
            "items": [_item_to_dict(i) for i in result.items],
            "total": result.total,
        }
    finally:
        reader.close()


def _handle_read(key: str) -> dict:
    reader = _get_reader()
    try:
        item = reader.get_item(key)
        if item is None:
            raise ValueError(f"Item '{key}' not found")
        notes = reader.get_notes(key)
        return {
            "item": _item_to_dict(item),
            "notes": [_note_to_dict(n) for n in notes],
        }
    finally:
        reader.close()


def _handle_pdf(key: str, start_page: int | None, end_page: int | None) -> dict:
    reader = _get_reader()
    try:
        att = reader.get_pdf_attachment(key)
        if att is None:
            raise ValueError(f"No PDF attachment found for item '{key}'")
        cfg = load_config()
        data_dir = get_data_dir(cfg)
        pdf_path = data_dir / "storage" / att.key / att.filename
        pages = (start_page, end_page) if start_page is not None and end_page is not None else None
        text = extract_text_from_pdf(pdf_path, pages=pages)
        return {
            "text": text,
            "filename": att.filename,
            "key": att.key,
        }
    finally:
        reader.close()


def _handle_summarize(key: str) -> dict:
    reader = _get_reader()
    try:
        item = reader.get_item(key)
        if item is None:
            raise ValueError(f"Item '{key}' not found")
        notes = reader.get_notes(key)
        return {
            "title": item.title,
            "authors": [c.full_name for c in item.creators],
            "year": item.date,
            "doi": item.doi,
            "abstract": item.abstract,
            "tags": item.tags,
            "notes": [n.content[:500] for n in notes],
        }
    finally:
        reader.close()


def _handle_export(key: str, fmt: str) -> dict:
    reader = _get_reader()
    try:
        citation = reader.export_citation(key, fmt=fmt)
        if citation is None:
            raise ValueError(f"Item '{key}' not found or format '{fmt}' not supported")
        return {
            "citation": citation,
            "format": fmt,
            "key": key,
        }
    finally:
        reader.close()


def _handle_relate(key: str, limit: int) -> dict:
    reader = _get_reader()
    try:
        items = reader.get_related_items(key, limit=limit)
        return {
            "items": [_item_to_dict(i) for i in items],
            "source_key": key,
        }
    finally:
        reader.close()


def _handle_note_view(key: str) -> dict:
    reader = _get_reader()
    try:
        notes = reader.get_notes(key)
        return {
            "notes": [_note_to_dict(n) for n in notes],
            "parent_key": key,
        }
    finally:
        reader.close()


def _handle_tag_view(key: str) -> dict:
    reader = _get_reader()
    try:
        item = reader.get_item(key)
        if item is None:
            raise ValueError(f"Item '{key}' not found")
        return {
            "tags": item.tags,
            "key": key,
            "title": item.title,
        }
    finally:
        reader.close()


def _handle_collection_list() -> dict:
    reader = _get_reader()
    try:
        collections = reader.get_collections()
        return {
            "collections": [_collection_to_dict(c) for c in collections],
        }
    finally:
        reader.close()


def _handle_collection_items(collection_key: str) -> dict:
    reader = _get_reader()
    try:
        items = reader.get_collection_items(collection_key)
        return {
            "items": [_item_to_dict(i) for i in items],
            "collection_key": collection_key,
        }
    finally:
        reader.close()


# ---------------------------------------------------------------------------
# MCP tool definitions
# ---------------------------------------------------------------------------


@mcp.tool()
def search(query: str, collection: str | None = None, limit: int = 50) -> dict:
    """Search the Zotero library by title, author, tag, or full text.

    Args:
        query: Search query string.
        collection: Optional collection name to filter results.
        limit: Maximum number of results (default 50).
    """
    return _handle_search(query, collection, limit)


@mcp.tool()
def list_items(limit: int = 50) -> dict:
    """List all items in the Zotero library.

    Args:
        limit: Maximum number of items to return (default 50).
    """
    return _handle_list_items(limit)


@mcp.tool()
def read(key: str) -> dict:
    """Read full details of a Zotero item including its notes.

    Args:
        key: The Zotero item key (e.g. 'ABC123').
    """
    return _handle_read(key)


@mcp.tool()
def pdf(key: str, start_page: int | None = None, end_page: int | None = None) -> dict:
    """Extract text from the PDF attachment of a Zotero item.

    Args:
        key: The Zotero item key.
        start_page: Optional first page to extract (1-indexed).
        end_page: Optional last page to extract (inclusive).
    """
    return _handle_pdf(key, start_page, end_page)


@mcp.tool()
def summarize(key: str) -> dict:
    """Get a structured summary of a Zotero item for AI consumption.

    Args:
        key: The Zotero item key.
    """
    return _handle_summarize(key)


@mcp.tool()
def export(key: str, fmt: str = "bibtex") -> dict:
    """Export citation for a Zotero item.

    Args:
        key: The Zotero item key.
        fmt: Citation format (default 'bibtex').
    """
    return _handle_export(key, fmt)


@mcp.tool()
def relate(key: str, limit: int = 20) -> dict:
    """Find items related to a given Zotero item.

    Args:
        key: The Zotero item key.
        limit: Maximum number of related items (default 20).
    """
    return _handle_relate(key, limit)


@mcp.tool()
def note_view(key: str) -> dict:
    """View all notes attached to a Zotero item.

    Args:
        key: The Zotero item key.
    """
    return _handle_note_view(key)


@mcp.tool()
def tag_view(key: str) -> dict:
    """View tags for a Zotero item.

    Args:
        key: The Zotero item key.
    """
    return _handle_tag_view(key)


@mcp.tool()
def collection_list() -> dict:
    """List all collections in the Zotero library."""
    return _handle_collection_list()


@mcp.tool()
def collection_items(collection_key: str) -> dict:
    """List all items in a specific Zotero collection.

    Args:
        collection_key: The collection key.
    """
    return _handle_collection_items(collection_key)
