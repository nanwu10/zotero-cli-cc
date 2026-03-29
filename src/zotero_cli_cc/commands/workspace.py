from __future__ import annotations

import json
import time
from datetime import datetime, timezone

import click

from zotero_cli_cc.config import get_data_dir, load_config, load_embedding_config, resolve_library_id
from zotero_cli_cc.core.rag import (
    bm25_score_chunks,
    build_metadata_chunk,
    chunk_text,
    compute_term_frequencies,
    convert_pdf_to_text,
    embed_texts,
    reciprocal_rank_fusion,
    semantic_score_chunks,
    tokenize,
)
from zotero_cli_cc.core.rag_index import RagIndex
from zotero_cli_cc.core.reader import ZoteroReader
from zotero_cli_cc.core.workspace import (
    delete_workspace,
    list_workspaces,
    load_workspace,
    save_workspace,
    validate_name,
    workspace_exists,
    workspaces_dir,
    Workspace,
)
from zotero_cli_cc.formatter import format_error, format_items
from zotero_cli_cc.models import ErrorInfo


@click.group("workspace")
def workspace_group() -> None:
    """Manage local workspaces for organizing papers by topic."""
    pass


@workspace_group.command("new")
@click.argument("name")
@click.option("--description", "-d", default="", help="Workspace description (topic context)")
@click.pass_context
def workspace_new(ctx: click.Context, name: str, description: str) -> None:
    """Create a new workspace."""
    json_out = ctx.obj.get("json", False)
    if not validate_name(name):
        click.echo(
            format_error(
                ErrorInfo(
                    message=f"Invalid workspace name: '{name}'",
                    context="workspace new",
                    hint="Use kebab-case (e.g., llm-safety, protein-folding)",
                ),
                output_json=json_out,
            )
        )
        return
    if workspace_exists(name):
        click.echo(
            format_error(
                ErrorInfo(
                    message=f"Workspace '{name}' already exists",
                    context="workspace new",
                    hint=f"Use 'zot workspace show {name}' to view it",
                ),
                output_json=json_out,
            )
        )
        return
    ws = Workspace(
        name=name,
        created=datetime.now(timezone.utc).isoformat(),
        description=description,
    )
    save_workspace(ws)
    click.echo(f"Workspace created: {name}")


@workspace_group.command("delete")
@click.argument("name")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
@click.pass_context
def workspace_delete(ctx: click.Context, name: str, yes: bool) -> None:
    """Delete a workspace."""
    json_out = ctx.obj.get("json", False)
    if not workspace_exists(name):
        click.echo(
            format_error(
                ErrorInfo(
                    message=f"Workspace '{name}' not found",
                    context="workspace delete",
                    hint="Use 'zot workspace list' to see available workspaces",
                ),
                output_json=json_out,
            )
        )
        return
    no_interaction = ctx.obj.get("no_interaction", False)
    if not yes and not no_interaction:
        if not click.confirm(f"Delete workspace '{name}'?"):
            click.echo("Cancelled.")
            return
    delete_workspace(name)
    click.echo(f"Workspace deleted: {name}")


@workspace_group.command("add")
@click.argument("name")
@click.argument("keys", nargs=-1, required=True)
@click.pass_context
def workspace_add(ctx: click.Context, name: str, keys: tuple[str, ...]) -> None:
    """Add items to a workspace by Zotero key."""
    json_out = ctx.obj.get("json", False)
    if not workspace_exists(name):
        click.echo(
            format_error(
                ErrorInfo(
                    message=f"Workspace '{name}' not found",
                    context="workspace add",
                    hint="Use 'zot workspace new' to create it first",
                ),
                output_json=json_out,
            )
        )
        return

    cfg = load_config(profile=ctx.obj.get("profile"))
    data_dir = get_data_dir(cfg)
    db_path = data_dir / "zotero.sqlite"
    library_id = resolve_library_id(db_path, ctx.obj)
    reader = ZoteroReader(db_path, library_id=library_id)
    try:
        ws = load_workspace(name)
        added = 0
        for key in keys:
            item = reader.get_item(key)
            if item is None:
                click.echo(f"Warning: item '{key}' not found in Zotero library, skipped")
                continue
            if ws.add_item(key, item.title):
                added += 1
            else:
                click.echo(f"Skipped: '{key}' already in workspace")
        save_workspace(ws)
        click.echo(f"Added {added} item(s) to workspace '{name}'")
    finally:
        reader.close()


@workspace_group.command("remove")
@click.argument("name")
@click.argument("keys", nargs=-1, required=True)
@click.pass_context
def workspace_remove(ctx: click.Context, name: str, keys: tuple[str, ...]) -> None:
    """Remove items from a workspace by key."""
    json_out = ctx.obj.get("json", False)
    if not workspace_exists(name):
        click.echo(
            format_error(
                ErrorInfo(
                    message=f"Workspace '{name}' not found",
                    context="workspace remove",
                    hint="Use 'zot workspace list' to see available workspaces",
                ),
                output_json=json_out,
            )
        )
        return
    ws = load_workspace(name)
    removed = 0
    for key in keys:
        if ws.remove_item(key):
            removed += 1
    save_workspace(ws)
    click.echo(f"Removed {removed} item(s) from workspace '{name}'")


@workspace_group.command("list")
@click.pass_context
def workspace_list(ctx: click.Context) -> None:
    """List all workspaces."""
    json_out = ctx.obj.get("json", False)
    workspaces = list_workspaces()
    if not workspaces:
        click.echo("No workspaces found. Create one with: zot workspace new <name>")
        return
    if json_out:
        data = [
            {
                "name": ws.name,
                "description": ws.description,
                "items": len(ws.items),
                "created": ws.created,
            }
            for ws in workspaces
        ]
        click.echo(json.dumps(data, indent=2, ensure_ascii=False))
        return

    from io import StringIO

    from rich.console import Console
    from rich.table import Table

    buf = StringIO()
    console = Console(file=buf, force_terminal=False, width=120)
    table = Table(show_header=True, header_style="bold")
    table.add_column("Name", style="cyan", width=20)
    table.add_column("Description", width=50)
    table.add_column("Items", justify="right", width=8)
    table.add_column("Created", width=20)
    for ws in workspaces:
        desc = ws.description[:47] + "..." if len(ws.description) > 50 else ws.description
        created = ws.created[:10] if len(ws.created) >= 10 else ws.created
        table.add_row(ws.name, desc, str(len(ws.items)), created)
    console.print(table)
    click.echo(buf.getvalue().rstrip())


@workspace_group.command("show")
@click.argument("name")
@click.pass_context
def workspace_show(ctx: click.Context, name: str) -> None:
    """Show items in a workspace."""
    json_out = ctx.obj.get("json", False)
    detail = ctx.obj.get("detail", "standard")
    limit = ctx.obj.get("limit", 50)

    if not workspace_exists(name):
        click.echo(
            format_error(
                ErrorInfo(
                    message=f"Workspace '{name}' not found",
                    context="workspace show",
                    hint="Use 'zot workspace list' to see available workspaces",
                ),
                output_json=json_out,
            )
        )
        return

    ws = load_workspace(name)
    if not ws.items:
        click.echo(f"Workspace '{name}' is empty. Use 'zot workspace add {name} KEY' to add items.")
        return

    cfg = load_config(profile=ctx.obj.get("profile"))
    data_dir = get_data_dir(cfg)
    db_path = data_dir / "zotero.sqlite"
    library_id = resolve_library_id(db_path, ctx.obj)
    reader = ZoteroReader(db_path, library_id=library_id)
    try:
        items = []
        missing = []
        for ws_item in ws.items[:limit]:
            item = reader.get_item(ws_item.key)
            if item is not None:
                items.append(item)
            else:
                missing.append(ws_item.key)
        if items:
            click.echo(format_items(items, output_json=json_out, detail=detail))
        for key in missing:
            click.echo(f"Warning: item '{key}' not found in Zotero library (may have been deleted)")
    finally:
        reader.close()


@workspace_group.command("index")
@click.argument("name")
@click.option("--force", is_flag=True, help="Rebuild index from scratch")
@click.pass_context
def workspace_index(ctx: click.Context, name: str, force: bool) -> None:
    """Build RAG index for a workspace."""
    json_out = ctx.obj.get("json", False)
    if not workspace_exists(name):
        click.echo(
            format_error(
                ErrorInfo(
                    message=f"Workspace '{name}' not found",
                    context="workspace index",
                    hint="Use 'zot workspace list' to see available workspaces",
                ),
                output_json=json_out,
            )
        )
        return

    ws = load_workspace(name)
    if not ws.items:
        click.echo(f"Workspace '{name}' is empty. Add items first with: zot workspace add {name} KEY")
        return

    cfg = load_config(profile=ctx.obj.get("profile"))
    data_dir = get_data_dir(cfg)
    db_path = data_dir / "zotero.sqlite"
    library_id = resolve_library_id(db_path, ctx.obj)
    reader = ZoteroReader(db_path, library_id=library_id)

    idx_path = workspaces_dir() / f"{name}.idx.sqlite"
    idx = RagIndex(idx_path)

    try:
        if force:
            idx.clear()

        already_indexed = idx.get_indexed_keys()
        to_index = [item for item in ws.items if item.key not in already_indexed]

        if not to_index:
            click.echo(f"Index for '{name}' is up to date ({len(already_indexed)} item(s) indexed).")
            return

        t0 = time.monotonic()
        total_chunks = 0
        all_chunk_ids: list[int] = []
        all_chunk_texts: list[str] = []

        for ws_item in to_index:
            item = reader.get_item(ws_item.key)
            if item is None:
                click.echo(f"Warning: item '{ws_item.key}' not found in Zotero, skipped")
                continue

            # Build metadata chunk
            authors = ", ".join(c.full_name for c in item.creators)
            meta_text = build_metadata_chunk(item.title, authors, item.abstract, item.tags)
            chunk_id = idx.insert_chunk(ws_item.key, "metadata", meta_text)
            tfs = compute_term_frequencies(tokenize(meta_text))
            idx.insert_bm25_terms(chunk_id, tfs)
            all_chunk_ids.append(chunk_id)
            all_chunk_texts.append(meta_text)
            total_chunks += 1

            # Try PDF
            att = reader.get_pdf_attachment(ws_item.key)
            if att is not None:
                pdf_path = data_dir / "storage" / att.key / att.filename
                if pdf_path.exists():
                    try:
                        pdf_text = convert_pdf_to_text(pdf_path)
                        chunks = chunk_text(pdf_text, item.title)
                        for chunk_content in chunks:
                            cid = idx.insert_chunk(ws_item.key, "pdf", chunk_content)
                            tfs = compute_term_frequencies(tokenize(chunk_content))
                            idx.insert_bm25_terms(cid, tfs)
                            all_chunk_ids.append(cid)
                            all_chunk_texts.append(chunk_content)
                            total_chunks += 1
                    except Exception:
                        pass  # skip PDF extraction errors silently

        # Update BM25 statistics
        all_chunks = idx.get_all_chunks()
        total_docs = len(all_chunks)
        if total_docs > 0:
            total_len = sum(len(tokenize(c["content"])) for c in all_chunks)
            avg_doc_len = total_len / total_docs
        else:
            avg_doc_len = 1.0
        idx.set_meta("total_docs", str(total_docs))
        idx.set_meta("avg_doc_len", str(avg_doc_len))
        idx.set_meta("chunk_count", str(total_docs))
        idx.set_meta("indexed_at", datetime.now(timezone.utc).isoformat())

        # Embeddings if configured
        mode_label = "BM25"
        emb_cfg = load_embedding_config()
        if emb_cfg.is_configured and all_chunk_texts:
            try:
                vectors = embed_texts(all_chunk_texts, emb_cfg)
                if vectors:
                    for cid, vec in zip(all_chunk_ids, vectors):
                        idx.set_embedding(cid, vec)
                    mode_label = "BM25 + embeddings"
            except Exception:
                pass  # embedding failures are non-fatal

        elapsed = time.monotonic() - t0
        click.echo(
            f"Indexed {len(to_index)} item(s) ({total_chunks} chunks) "
            f"in {elapsed:.1f}s [{mode_label}]"
        )
    finally:
        idx.close()
        reader.close()


@workspace_group.command("query")
@click.argument("question")
@click.option("--workspace", "ws_name", required=True, help="Workspace to query")
@click.option("--top-k", default=5, help="Number of results (default: 5)")
@click.option(
    "--mode",
    type=click.Choice(["auto", "bm25", "semantic", "hybrid"]),
    default="auto",
    help="Retrieval mode",
)
@click.pass_context
def workspace_query(
    ctx: click.Context, question: str, ws_name: str, top_k: int, mode: str
) -> None:
    """Query workspace papers with natural language."""
    json_out = ctx.obj.get("json", False)
    if not workspace_exists(ws_name):
        click.echo(
            format_error(
                ErrorInfo(
                    message=f"Workspace '{ws_name}' not found",
                    context="workspace query",
                    hint="Use 'zot workspace list' to see available workspaces",
                ),
                output_json=json_out,
            )
        )
        return

    idx_path = workspaces_dir() / f"{ws_name}.idx.sqlite"
    if not idx_path.exists():
        click.echo(
            format_error(
                ErrorInfo(
                    message=f"No index found for workspace '{ws_name}'",
                    context="workspace query",
                    hint=f"Run 'zot workspace index {ws_name}' first",
                ),
                output_json=json_out,
            )
        )
        return

    idx = RagIndex(idx_path)
    try:
        # Determine effective mode
        has_embeddings = len(idx.get_all_embeddings()) > 0
        if mode == "auto":
            effective_mode = "hybrid" if has_embeddings else "bm25"
        else:
            effective_mode = mode

        bm25_results: list[tuple[int, float, dict]] = []
        semantic_results: list[tuple[int, float, dict]] = []

        if effective_mode in ("bm25", "hybrid"):
            bm25_results = bm25_score_chunks(idx, question)

        if effective_mode in ("semantic", "hybrid") and has_embeddings:
            emb_cfg = load_embedding_config()
            if emb_cfg.is_configured:
                try:
                    q_vecs = embed_texts([question], emb_cfg)
                    if q_vecs:
                        semantic_results = semantic_score_chunks(idx, q_vecs[0])
                except Exception:
                    pass

        # Merge results
        if effective_mode == "hybrid" and bm25_results and semantic_results:
            merged = reciprocal_rank_fusion(bm25_results, semantic_results)
        elif semantic_results and effective_mode in ("semantic", "hybrid"):
            merged = semantic_results
        else:
            merged = bm25_results

        top = merged[:top_k]

        if not top:
            if json_out:
                click.echo("[]")
            else:
                click.echo("No results found.")
            return

        if json_out:
            data = [
                {
                    "rank": i + 1,
                    "score": round(score, 4),
                    "item_key": chunk["item_key"],
                    "source": chunk["source"],
                    "content": chunk["content"][:500],
                }
                for i, (_cid, score, chunk) in enumerate(top)
            ]
            click.echo(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            for i, (_cid, score, chunk) in enumerate(top):
                preview = chunk["content"][:120].replace("\n", " ")
                click.echo(
                    f"[{i + 1}] Score: {score:.2f} | {chunk['item_key']} | {chunk['source']}"
                )
                click.echo(f"    {preview}...")
    finally:
        idx.close()
