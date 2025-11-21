import pytest
from pathlib import Path
from rag.ingestion import parse_markdown_file, chunk_by_headers, clean_markdown
from rag.models import DocumentChunk


def test_clean_markdown():
    text = "# Header\n\n**Bold** and *italic* text with `code`"
    cleaned = clean_markdown(text)
    assert "Header" in cleaned
    assert "**" not in cleaned
    assert "*" not in cleaned
    assert "`" not in cleaned


def test_chunk_by_headers():
    content = """# Main Title

This is intro content.

## Section 1

Content for section 1.

## Section 2

Content for section 2.
"""
    
    chunks = chunk_by_headers(content, "test.md", "Test Document")
    
    assert len(chunks) > 0
    assert any("Section 1" in chunk.title for chunk in chunks)
    assert any("Section 2" in chunk.title for chunk in chunks)


def test_chunk_minimum_length():
    content = "Short"
    chunks = chunk_by_headers(content, "test.md", "Test")
    
    assert len(chunks) == 0


def test_chunk_metadata():
    content = "## Test Section\n\nTest content that is long enough to be included."
    chunks = chunk_by_headers(content, "test.md", "Test Doc")
    
    assert len(chunks) > 0
    assert chunks[0].doc_path == "test.md"
    assert "section" in chunks[0].metadata

