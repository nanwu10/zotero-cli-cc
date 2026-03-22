from __future__ import annotations

from pathlib import Path

import pymupdf


class PdfExtractionError(Exception):
    """Raised when PDF text extraction fails."""
    pass


def extract_text_from_pdf(
    pdf_path: Path,
    pages: tuple[int, int] | None = None,
) -> str:
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    try:
        doc = pymupdf.open(str(pdf_path))
    except Exception as e:
        raise PdfExtractionError(f"Cannot open PDF: {e}") from e
    try:
        if pages:
            start, end = pages
            if start > len(doc):
                raise PdfExtractionError(
                    f"Start page {start} exceeds document length ({len(doc)} pages)"
                )
            page_range = range(start - 1, min(end, len(doc)))
        else:
            page_range = range(len(doc))
        texts = []
        for i in page_range:
            texts.append(doc[i].get_text())
        return "\n".join(texts)
    except PdfExtractionError:
        raise
    except Exception as e:
        raise PdfExtractionError(f"Failed to extract text: {e}") from e
    finally:
        doc.close()
