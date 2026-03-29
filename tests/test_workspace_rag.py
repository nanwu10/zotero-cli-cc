"""Tests for workspace RAG CLI commands."""

from __future__ import annotations

import json
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from zotero_cli_cc.cli import main

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _invoke(args: list[str], json_output: bool = False):
    runner = CliRunner()
    base = ["--json"] if json_output else []
    env = {"ZOT_DATA_DIR": str(FIXTURES_DIR)}
    return runner.invoke(main, base + args, env=env)


def _patch_ws_dir(tmp_path):
    """Patch workspaces_dir in both the core module and the commands module."""
    stack = ExitStack()
    stack.enter_context(
        patch("zotero_cli_cc.core.workspace.workspaces_dir", return_value=tmp_path)
    )
    stack.enter_context(
        patch("zotero_cli_cc.commands.workspace.workspaces_dir", return_value=tmp_path)
    )
    return stack


class TestWorkspaceIndex:
    def test_index_workspace(self, tmp_path):
        with _patch_ws_dir(tmp_path):
            _invoke(["workspace", "new", "test-idx"])
            _invoke(["workspace", "add", "test-idx", "ATTN001"])
            result = _invoke(["workspace", "index", "test-idx"])
        assert result.exit_code == 0
        assert "Indexed" in result.output
        idx_path = tmp_path / "test-idx.idx.sqlite"
        assert idx_path.exists()

    def test_index_nonexistent_workspace(self, tmp_path):
        with _patch_ws_dir(tmp_path):
            result = _invoke(["workspace", "index", "nope"])
        assert "not found" in result.output

    def test_index_empty_workspace(self, tmp_path):
        with _patch_ws_dir(tmp_path):
            _invoke(["workspace", "new", "empty-ws"])
            result = _invoke(["workspace", "index", "empty-ws"])
        assert "empty" in result.output.lower() or "Add items" in result.output

    def test_index_force_rebuild(self, tmp_path):
        with _patch_ws_dir(tmp_path):
            _invoke(["workspace", "new", "test-idx"])
            _invoke(["workspace", "add", "test-idx", "ATTN001"])
            _invoke(["workspace", "index", "test-idx"])
            result = _invoke(["workspace", "index", "test-idx", "--force"])
        assert result.exit_code == 0
        assert "Indexed" in result.output

    def test_index_incremental(self, tmp_path):
        with _patch_ws_dir(tmp_path):
            _invoke(["workspace", "new", "test-idx"])
            _invoke(["workspace", "add", "test-idx", "ATTN001"])
            _invoke(["workspace", "index", "test-idx"])
            # Second index without force should say up to date
            result = _invoke(["workspace", "index", "test-idx"])
        assert "up to date" in result.output


class TestWorkspaceQuery:
    def test_query_workspace(self, tmp_path):
        with _patch_ws_dir(tmp_path):
            _invoke(["workspace", "new", "test-q"])
            _invoke(["workspace", "add", "test-q", "ATTN001"])
            _invoke(["workspace", "index", "test-q"])
            result = _invoke(["workspace", "query", "attention", "--workspace", "test-q"])
        assert result.exit_code == 0
        assert "ATTN001" in result.output

    def test_query_json_output(self, tmp_path):
        with _patch_ws_dir(tmp_path):
            _invoke(["workspace", "new", "test-q"])
            _invoke(["workspace", "add", "test-q", "ATTN001"])
            _invoke(["workspace", "index", "test-q"])
            result = _invoke(
                ["workspace", "query", "attention", "--workspace", "test-q"],
                json_output=True,
            )
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) > 0
        assert "item_key" in data[0]

    def test_query_no_results(self, tmp_path):
        with _patch_ws_dir(tmp_path):
            _invoke(["workspace", "new", "test-q"])
            _invoke(["workspace", "add", "test-q", "ATTN001"])
            _invoke(["workspace", "index", "test-q"])
            result = _invoke(
                ["workspace", "query", "xyznonexistent", "--workspace", "test-q"]
            )
        assert "No results" in result.output or "[]" in result.output

    def test_query_no_index(self, tmp_path):
        with _patch_ws_dir(tmp_path):
            _invoke(["workspace", "new", "test-q"])
            result = _invoke(["workspace", "query", "test", "--workspace", "test-q"])
        assert "index" in result.output.lower()

    def test_query_nonexistent_workspace(self, tmp_path):
        with _patch_ws_dir(tmp_path):
            result = _invoke(["workspace", "query", "test", "--workspace", "nope"])
        assert "not found" in result.output
