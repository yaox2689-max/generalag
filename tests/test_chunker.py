import pytest
from knowledge.chunker import chunk_text, ChunkingConfig


class TestChunker:
    def test_basic_chunking(self):
        text = "This is sentence one. " * 50
        chunks = chunk_text(text, source="test.txt", config=ChunkingConfig(chunk_size=200, chunk_overlap=20))
        assert len(chunks) > 1
        for chunk in chunks:
            assert chunk.metadata["source"] == "test.txt"

    def test_short_text_single_chunk(self):
        text = "This is a short sentence."
        chunks = chunk_text(text, source="test.txt")
        assert len(chunks) == 1
        assert chunks[0].text == text

    def test_chinese_text_chunking(self):
        text = "这是第一段内容。\n\n这是第二段内容。\n\n这是第三段内容。"
        chunks = chunk_text(text, source="zh.txt", config=ChunkingConfig(chunk_size=20, chunk_overlap=5))
        assert len(chunks) >= 1

    def test_chunk_metadata(self):
        text = "Hello world"
        chunks = chunk_text(text, source="doc.pdf")
        assert chunks[0].metadata["source"] == "doc.pdf"
        assert chunks[0].metadata["chunk_index"] == 0
        assert chunks[0].index == 0

    def test_default_config(self):
        text = "This is a paragraph. " * 100
        chunks = chunk_text(text)
        assert len(chunks) > 1
