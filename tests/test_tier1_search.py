"""Tests for Tier 1 search enhancements: type filter."""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from zotero_cli_cc.cli import main
from zotero_cli_cc.core.reader import ZoteroReader

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _invoke(args: list[str], json_output: bool = False):
    runner = CliRunner()
    base = ["--json"] if json_output else []
    env = {"ZOT_DATA_DIR": str(FIXTURES_DIR)}
    return runner.invoke(main, base + args, env=env)


class TestItemTypeFilter:
    def test_search_filter_by_type_journal(self):
        result = _invoke(["search", "attention", "--type", "journalArticle"], json_output=True)
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert all(i["item_type"] == "journalArticle" for i in data)

    def test_search_filter_by_type_book(self):
        result = _invoke(["search", "", "--type", "book"], json_output=True)
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) >= 1
        assert all(i["item_type"] == "book" for i in data)

    def test_search_filter_by_type_no_match(self):
        result = _invoke(["search", "attention", "--type", "thesis"], json_output=True)
        assert result.exit_code == 0
        assert result.output.strip() == "[]"

    def test_list_filter_by_type(self):
        result = _invoke(["list", "--type", "book"], json_output=True)
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert all(i["item_type"] == "book" for i in data)

    def test_reader_search_item_type(self):
        reader = ZoteroReader(FIXTURES_DIR / "zotero.sqlite")
        try:
            result = reader.search("", item_type="book")
            assert all(i.item_type == "book" for i in result.items)
        finally:
            reader.close()

    def test_type_filter_with_collection(self):
        result = _invoke(
            ["search", "", "--type", "journalArticle", "--collection", "Machine Learning"], json_output=True
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert all(i["item_type"] == "journalArticle" for i in data)
