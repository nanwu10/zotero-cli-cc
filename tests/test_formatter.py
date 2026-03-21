import json

from zotero_cli_cc.formatter import format_items, format_item_detail, format_collections, format_notes, format_error
from zotero_cli_cc.models import Item, Creator, Collection, Note


def _make_item(key="K1", title="Test") -> Item:
    return Item(
        key=key, item_type="journalArticle", title=title,
        creators=[Creator("John", "Doe", "author")],
        abstract="Abstract.", date="2025", url=None, doi="10.1/x",
        tags=["ML"], collections=[], date_added="2025-01-01",
        date_modified="2025-01-02", extra={},
    )


def test_format_items_json():
    items = [_make_item()]
    result = format_items(items, output_json=True)
    data = json.loads(result)
    assert len(data) == 1
    assert data[0]["key"] == "K1"


def test_format_items_table():
    items = [_make_item()]
    result = format_items(items, output_json=False)
    assert "K1" in result
    assert "Test" in result


def test_format_item_detail_json():
    item = _make_item()
    result = format_item_detail(item, notes=[], output_json=True)
    data = json.loads(result)
    assert data["title"] == "Test"


def test_format_item_detail_table():
    item = _make_item()
    result = format_item_detail(item, notes=[], output_json=False)
    assert "Test" in result
    assert "John Doe" in result


def test_format_collections_json():
    colls = [Collection(key="C1", name="ML", parent_key=None, children=[])]
    result = format_collections(colls, output_json=True)
    data = json.loads(result)
    assert data[0]["name"] == "ML"


def test_format_notes_json():
    notes = [Note(key="N1", parent_key="P1", content="Hello", tags=[])]
    result = format_notes(notes, output_json=True)
    data = json.loads(result)
    assert data[0]["content"] == "Hello"


def test_format_error_json_with_hint():
    from zotero_cli_cc.models import ErrorInfo
    err = ErrorInfo(message="Item 'XYZ' not found", context="read", hint="Run 'zot search' to find valid keys")
    result = format_error(err, output_json=True)
    data = json.loads(result)
    assert data["error"] == "Item 'XYZ' not found"
    assert data["context"] == "read"
    assert data["hint"] == "Run 'zot search' to find valid keys"


def test_format_error_text_with_hint():
    from zotero_cli_cc.models import ErrorInfo
    err = ErrorInfo(message="Item 'XYZ' not found", hint="Run 'zot search' to find valid keys")
    result = format_error(err, output_json=False)
    assert "Error: Item 'XYZ' not found" in result
    assert "Hint: Run 'zot search' to find valid keys" in result


def test_format_error_backward_compat_string():
    result = format_error("simple error", output_json=False)
    assert result == "Error: simple error"


def test_format_error_backward_compat_string_json():
    result = format_error("simple error", output_json=True)
    data = json.loads(result)
    assert data["error"] == "simple error"
