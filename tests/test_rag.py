"""Tests for RAG engine and index."""

from __future__ import annotations

import pytest

from zotero_cli_cc.core.rag_index import RagIndex


class TestRagIndex:
    def test_create_index(self, tmp_path):
        idx = RagIndex(tmp_path / "test.idx.sqlite")
        try:
            assert (tmp_path / "test.idx.sqlite").exists()
        finally:
            idx.close()

    def test_insert_and_get_chunks(self, tmp_path):
        idx = RagIndex(tmp_path / "test.idx.sqlite")
        try:
            idx.insert_chunk("ABC123", "metadata", "Title: Test Paper\nAbstract: about attention")
            idx.insert_chunk("ABC123", "pdf", "[Test Paper > Introduction] We study attention...")
            chunks = idx.get_all_chunks()
            assert len(chunks) == 2
            assert chunks[0]["item_key"] == "ABC123"
            assert chunks[0]["source"] == "metadata"
        finally:
            idx.close()

    def test_insert_bm25_terms(self, tmp_path):
        idx = RagIndex(tmp_path / "test.idx.sqlite")
        try:
            chunk_id = idx.insert_chunk("ABC123", "metadata", "attention mechanism")
            idx.insert_bm25_terms(chunk_id, {"attention": 1.0, "mechanism": 1.0})
            terms = idx.get_bm25_terms_for_chunk(chunk_id)
            assert "attention" in terms
        finally:
            idx.close()

    def test_set_and_get_meta(self, tmp_path):
        idx = RagIndex(tmp_path / "test.idx.sqlite")
        try:
            idx.set_meta("chunk_count", "42")
            idx.set_meta("has_embeddings", "false")
            assert idx.get_meta("chunk_count") == "42"
            assert idx.get_meta("has_embeddings") == "false"
            assert idx.get_meta("nonexistent") is None
        finally:
            idx.close()

    def test_insert_embedding(self, tmp_path):
        idx = RagIndex(tmp_path / "test.idx.sqlite")
        try:
            chunk_id = idx.insert_chunk("ABC123", "pdf", "some text")
            embedding = [0.1, 0.2, 0.3]
            idx.set_embedding(chunk_id, embedding)
            loaded = idx.get_embedding(chunk_id)
            assert len(loaded) == 3
            assert abs(loaded[0] - 0.1) < 1e-6
        finally:
            idx.close()

    def test_clear_index(self, tmp_path):
        idx = RagIndex(tmp_path / "test.idx.sqlite")
        try:
            idx.insert_chunk("ABC123", "metadata", "test")
            idx.clear()
            assert len(idx.get_all_chunks()) == 0
        finally:
            idx.close()

    def test_get_indexed_keys(self, tmp_path):
        idx = RagIndex(tmp_path / "test.idx.sqlite")
        try:
            idx.insert_chunk("ABC123", "metadata", "text a")
            idx.insert_chunk("DEF456", "metadata", "text b")
            idx.insert_chunk("ABC123", "pdf", "text c")
            keys = idx.get_indexed_keys()
            assert keys == {"ABC123", "DEF456"}
        finally:
            idx.close()
