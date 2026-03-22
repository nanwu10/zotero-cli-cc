from __future__ import annotations

import json

import click

from zotero_cli_cc.config import load_config, get_data_dir
from zotero_cli_cc.core.reader import ZoteroReader
from zotero_cli_cc.core.pdf_extractor import extract_text_from_pdf, PdfExtractionError
from zotero_cli_cc.formatter import format_error
from zotero_cli_cc.models import ErrorInfo


@click.command("pdf")
@click.argument("key")
@click.option("--pages", default=None, help="Page range, e.g. '1-5'")
@click.pass_context
def pdf_cmd(ctx: click.Context, key: str, pages: str | None) -> None:
    """Extract text from the PDF attachment."""
    cfg = load_config(profile=ctx.obj.get("profile"))
    json_out = ctx.obj.get("json", False)
    page_range = None
    if pages:
        try:
            parts = pages.split("-")
            start = int(parts[0])
            end = int(parts[1]) if len(parts) > 1 else start
            if start < 1 or end < start:
                raise ValueError(f"invalid range: start={start}, end={end}")
            page_range = (start, end)
        except ValueError:
            click.echo(format_error(ErrorInfo(message=f"Invalid page range '{pages}'", context="pdf", hint="Use format: '1-5' or '3' for a single page"), output_json=json_out))
            return
    data_dir = get_data_dir(cfg)
    db_path = data_dir / "zotero.sqlite"
    reader = ZoteroReader(db_path)
    try:
        att = reader.get_pdf_attachment(key)
        if att is None:
            click.echo(format_error(ErrorInfo(message=f"No PDF attachment found for '{key}'", context="pdf", hint="Check item details with: zot read KEY"), output_json=json_out))
            return
        pdf_path = data_dir / "storage" / att.key / att.filename
        if not pdf_path.exists():
            click.echo(format_error(ErrorInfo(message=f"PDF file not found at {pdf_path}", context="pdf", hint="The file may have been moved. Check Zotero storage directory"), output_json=json_out))
            return
        from zotero_cli_cc.core.pdf_cache import PdfCache
        cache = PdfCache()
        try:
            if page_range is None:
                cached = cache.get(pdf_path)
                if cached is not None:
                    text = cached
                else:
                    text = extract_text_from_pdf(pdf_path)
                    cache.put(pdf_path, text)
            else:
                text = extract_text_from_pdf(pdf_path, pages=page_range)
        except PdfExtractionError as e:
            cache.close()
            click.echo(format_error(ErrorInfo(message=str(e), context="pdf", hint="The PDF may be corrupted or password-protected"), output_json=json_out))
            return
        cache.close()
        if json_out:
            click.echo(json.dumps({"key": key, "pages": pages, "text": text}, ensure_ascii=False))
        else:
            click.echo(text)
    finally:
        reader.close()
