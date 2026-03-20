from pathlib import Path

import pytest

from zotero_cli_cc.core.pdf_extractor import extract_text_from_pdf

FIXTURES = Path(__file__).parent / "fixtures"


def test_extract_full_pdf():
    text = extract_text_from_pdf(FIXTURES / "test.pdf")
    assert "test PDF" in text


def test_extract_specific_pages():
    text = extract_text_from_pdf(FIXTURES / "test.pdf", pages=(1, 1))
    assert "test PDF" in text


def test_extract_nonexistent_pdf():
    with pytest.raises(FileNotFoundError):
        extract_text_from_pdf(FIXTURES / "nonexistent.pdf")
