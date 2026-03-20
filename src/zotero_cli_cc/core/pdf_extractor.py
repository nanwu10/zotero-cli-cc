from __future__ import annotations

from pathlib import Path

import pymupdf


def extract_text_from_pdf(
    pdf_path: Path,
    pages: tuple[int, int] | None = None,
) -> str:
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    doc = pymupdf.open(str(pdf_path))
    try:
        if pages:
            start, end = pages
            page_range = range(start - 1, min(end, len(doc)))
        else:
            page_range = range(len(doc))
        texts = []
        for i in page_range:
            texts.append(doc[i].get_text())
        return "\n".join(texts)
    finally:
        doc.close()
