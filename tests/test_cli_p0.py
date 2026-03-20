import json
from pathlib import Path

from click.testing import CliRunner

from zotero_cli_cc.cli import main


def _invoke(args: list[str], test_db_path: Path, json_output: bool = False):
    runner = CliRunner()
    base_args = ["--json"] if json_output else []
    env = {"ZOT_DATA_DIR": str(test_db_path.parent)}
    return runner.invoke(main, base_args + args, env=env)


class TestSearch:
    def test_search_finds_item(self, test_db_path):
        result = _invoke(["search", "attention"], test_db_path)
        assert result.exit_code == 0
        assert "ATTN001" in result.output

    def test_search_json(self, test_db_path):
        result = _invoke(["search", "attention"], test_db_path, json_output=True)
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert any(i["key"] == "ATTN001" for i in data)

    def test_search_no_results(self, test_db_path):
        result = _invoke(["search", "zzzznonexistent"], test_db_path)
        assert result.exit_code == 0
        assert "No results" in result.output

    def test_search_with_collection(self, test_db_path):
        result = _invoke(["search", "", "--collection", "Transformers"], test_db_path, json_output=True)
        data = json.loads(result.output)
        assert all(i["key"] == "ATTN001" for i in data)


class TestList:
    def test_list_all(self, test_db_path):
        result = _invoke(["list"], test_db_path)
        assert result.exit_code == 0
        assert "ATTN001" in result.output

    def test_list_with_collection(self, test_db_path):
        result = _invoke(["list", "--collection", "Machine Learning"], test_db_path, json_output=True)
        data = json.loads(result.output)
        assert len(data) >= 2

    def test_list_with_limit(self, test_db_path):
        result = _invoke(["--limit", "1", "list"], test_db_path, json_output=True)
        data = json.loads(result.output)
        assert len(data) == 1


class TestRead:
    def test_read_item(self, test_db_path):
        result = _invoke(["read", "ATTN001"], test_db_path)
        assert result.exit_code == 0
        assert "Attention Is All You Need" in result.output
        assert "Vaswani" in result.output

    def test_read_json(self, test_db_path):
        result = _invoke(["read", "ATTN001"], test_db_path, json_output=True)
        data = json.loads(result.output)
        assert data["title"] == "Attention Is All You Need"
        assert "notes" in data

    def test_read_nonexistent(self, test_db_path):
        result = _invoke(["read", "NONEXIST"], test_db_path)
        assert result.exit_code == 0
        assert "not found" in result.output.lower()


class TestExport:
    def test_export_bibtex(self, test_db_path):
        result = _invoke(["export", "ATTN001"], test_db_path)
        assert result.exit_code == 0
        assert "@article" in result.output
        assert "Attention" in result.output

    def test_export_json(self, test_db_path):
        result = _invoke(["export", "ATTN001", "--format", "json"], test_db_path)
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "title" in data
