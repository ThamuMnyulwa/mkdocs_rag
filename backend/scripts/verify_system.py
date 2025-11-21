"""
System verification script that tests the RAG pipeline without external API dependencies.
Mocks Google GenAI API calls to verify the system logic works correctly.
"""
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import List
import tempfile
import shutil

os.environ['GOOGLE_API_KEY'] = "mock_api_key_for_testing"

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Settings
from rag.models import DocumentChunk, RetrievedChunk
from rag.vector_store import VectorStore
from rag.ingestion import parse_markdown_file, chunk_by_headers, clean_markdown, embed_chunks
from rag.retriever import Retriever
import numpy as np


def generate_mock_embedding(text: str, dimension: int = 768) -> List[float]:
    """Generate a deterministic mock embedding based on text hash."""
    np.random.seed(hash(text) % (2**32))
    embedding = np.random.rand(dimension).tolist()
    return embedding


def create_mock_genai():
    """Create a mock for google.generativeai module."""
    mock_genai = MagicMock()
    
    def mock_embed_content(model, content, task_type):
        embedding = generate_mock_embedding(content)
        return {'embedding': embedding}
    
    mock_genai.embed_content = mock_embed_content
    
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "This is a generated answer based on the provided context. According to the documentation, the system processes queries using vector similarity search."
    mock_model.generate_content.return_value = mock_response
    mock_genai.GenerativeModel.return_value = mock_model
    
    mock_genai.configure = MagicMock()
    
    return mock_genai


class TestContext:
    """Context manager for test setup and teardown."""
    def __init__(self):
        self.temp_dir = None
        self.original_settings = None
        
    def __enter__(self):
        self.temp_dir = tempfile.mkdtemp()
        
        self.original_settings = {
            'chroma_persist_dir': os.environ.get('CHROMA_PERSIST_DIR'),
            'google_api_key': os.environ.get('GOOGLE_API_KEY')
        }
        
        os.environ['CHROMA_PERSIST_DIR'] = str(Path(self.temp_dir) / "chroma_db")
        os.environ['GOOGLE_API_KEY'] = "mock_api_key_for_testing"
        
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        
        for key, value in self.original_settings.items():
            if value is None:
                os.environ.pop(key.upper(), None)
            else:
                os.environ[key.upper()] = value


def test_markdown_parsing():
    """Test markdown file parsing and chunking."""
    print("\n[TEST 1] Testing Markdown Parsing and Chunking...")
    
    test_content = """# Database Maintenance

This is the introduction to database maintenance.

## Performance Monitoring

Monitor your database performance using these queries:

```sql
SELECT * FROM pg_stat_activity;
```

Check for slow queries regularly.

## Backup Procedures

Always backup before maintenance:

1. Stop applications
2. Create backup
3. Verify backup integrity
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
        f.write(test_content)
        temp_file = f.name
    
    try:
        temp_path = Path(temp_file)
        
        with patch.object(Settings, 'docs_path_absolute', Path(temp_path.parent)):
            doc_path, title, content = parse_markdown_file(temp_path)
        
        print(f"  ✓ Parsed file: {doc_path}")
        print(f"  ✓ Title: {title}")
        print(f"  ✓ Content length: {len(content)} chars")
        
        chunks = chunk_by_headers(content, doc_path, title)
        print(f"  ✓ Created {len(chunks)} chunks")
        
        for i, chunk in enumerate(chunks):
            print(f"    - Chunk {i+1}: {chunk.title[:50]}... ({len(chunk.text)} chars)")
        
        assert len(chunks) > 0, "Should create at least one chunk"
        assert all(len(chunk.text) > 0 for chunk in chunks), "All chunks should have content"
        
        print("  ✓ Markdown parsing test PASSED")
        return True
        
    finally:
        os.unlink(temp_file)


def test_vector_store_operations(mock_genai):
    """Test vector store operations with mocked embeddings."""
    print("\n[TEST 2] Testing Vector Store Operations...")
    
    with TestContext():
        with patch('rag.ingestion.genai', mock_genai):
            vector_store = VectorStore()
            
            print(f"  ✓ Vector store initialized")
            print(f"  ✓ Initial count: {vector_store.count()} documents")
            
            test_chunks = [
                DocumentChunk(
                    id="chunk1",
                    doc_path="test/doc1.md",
                    title="Test Document 1",
                    text="This document explains how to configure database connections and connection pooling.",
                    metadata={"section": "Configuration"}
                ),
                DocumentChunk(
                    id="chunk2",
                    doc_path="test/doc2.md",
                    title="Test Document 2",
                    text="Security policies require two-factor authentication for all production access.",
                    metadata={"section": "Security"}
                ),
                DocumentChunk(
                    id="chunk3",
                    doc_path="test/doc3.md",
                    title="Test Document 3",
                    text="Incident response procedures start with identifying the severity level of the incident.",
                    metadata={"section": "Incidents"}
                )
            ]
            
            chunks_with_embeddings = embed_chunks(test_chunks)
            
            for i, chunk in enumerate(chunks_with_embeddings):
                assert chunk.embedding is not None, f"Chunk {i+1} should have embedding"
                assert len(chunk.embedding) > 0, f"Chunk {i+1} embedding should not be empty"
            
            print(f"  ✓ Generated embeddings for {len(chunks_with_embeddings)} chunks")
            
            vector_store.add_chunks(chunks_with_embeddings)
            print(f"  ✓ Added chunks to vector store")
            print(f"  ✓ Final count: {vector_store.count()} documents")
            
            query_embedding = generate_mock_embedding("How do I configure database connections?")
            results = vector_store.search(query_embedding, top_k=2)
            
            print(f"  ✓ Search returned {len(results)} results")
            for i, result in enumerate(results):
                print(f"    - Result {i+1}: {result.title} (score: {result.score:.3f})")
            
            assert len(results) > 0, "Search should return results"
            assert all(isinstance(r, RetrievedChunk) for r in results), "Results should be RetrievedChunk instances"
            
            print("  ✓ Vector store operations test PASSED")
            return vector_store, chunks_with_embeddings


def test_retriever(mock_genai):
    """Test the Retriever with mocked generation."""
    print("\n[TEST 3] Testing Retriever Query Flow...")
    
    with TestContext():
        with patch('rag.ingestion.genai', mock_genai):
            with patch('rag.retriever.genai', mock_genai):
                vector_store = VectorStore()
                
                test_chunks = [
                    DocumentChunk(
                        id="db_chunk",
                        doc_path="runbooks/database-maintenance.md",
                        title="Database Maintenance",
                        text="To monitor database performance, use pg_stat_activity. Check for slow queries and optimize indexes regularly.",
                        metadata={"section": "Performance"}
                    ),
                    DocumentChunk(
                        id="security_chunk",
                        doc_path="policies/security.md",
                        title="Security Policy",
                        text="All production systems require multi-factor authentication. Access must be requested through the ticketing system.",
                        metadata={"section": "Access Control"}
                    )
                ]
                
                chunks_with_embeddings = embed_chunks(test_chunks)
                vector_store.add_chunks(chunks_with_embeddings)
                
                print(f"  ✓ Populated vector store with {vector_store.count()} chunks")
                
                retriever = Retriever(vector_store)
                print(f"  ✓ Initialized retriever")
                
                import asyncio
                
                async def run_query():
                    result = await retriever.query("How do I monitor database performance?")
                    return result
                
                result = asyncio.run(run_query())
                
                print(f"  ✓ Query executed successfully")
                print(f"  ✓ Answer length: {len(result.answer)} chars")
                print(f"  ✓ Retrieved {len(result.chunks)} source chunks")
                
                for i, chunk in enumerate(result.chunks):
                    print(f"    - Source {i+1}: {chunk.title} (score: {chunk.score:.3f})")
                
                assert result.answer, "Should generate an answer"
                assert len(result.chunks) > 0, "Should retrieve source chunks"
                assert result.query == "How do I monitor database performance?", "Should preserve query"
                
                print("  ✓ Retriever test PASSED")
                return True


def test_full_pipeline(mock_genai):
    """Test the complete ingestion and retrieval pipeline."""
    print("\n[TEST 4] Testing Full Pipeline (Ingestion + Retrieval)...")
    
    with TestContext() as ctx:
        with patch('rag.ingestion.genai', mock_genai):
            with patch('rag.retriever.genai', mock_genai):
                docs_dir = Path(ctx.temp_dir) / "docs"
                docs_dir.mkdir()
                
                test_docs = {
                    "incident-response.md": """---
title: Incident Response Runbook
---

# Incident Response

## Severity Levels

P0: Critical system outage affecting all users
P1: Major functionality impaired
P2: Minor issues with workarounds available

## Response Procedures

1. Assess severity
2. Notify stakeholders
3. Begin mitigation
""",
                    "deployment.md": """---
title: Deployment Guide
---

# Deployment Process

## Pre-deployment Checklist

- Run all tests
- Review changes
- Backup database
- Notify team

## Deployment Steps

1. Merge to main branch
2. Tag release
3. Deploy to staging
4. Verify and promote to production
"""
                }
                
                for filename, content in test_docs.items():
                    (docs_dir / filename).write_text(content, encoding='utf-8')
                
                print(f"  ✓ Created {len(test_docs)} test documents")
                
                with patch('config.settings.docs_path', str(docs_dir)):
                    vector_store = VectorStore()
                    
                    from rag.ingestion import ingest_docs
                    import asyncio
                    
                    num_chunks = asyncio.run(ingest_docs(vector_store))
                    
                    print(f"  ✓ Ingested {num_chunks} chunks from {len(test_docs)} documents")
                    print(f"  ✓ Vector store count: {vector_store.count()}")
                    
                    retriever = Retriever(vector_store)
                    
                    async def test_queries():
                        queries = [
                            "What are the severity levels for incidents?",
                            "How do I deploy to production?",
                            "What is the backup procedure?"
                        ]
                        
                        for query in queries:
                            result = await retriever.query(query)
                            print(f"\n  Query: '{query}'")
                            print(f"  Answer preview: {result.answer[:100]}...")
                            print(f"  Sources: {len(result.chunks)}")
                            
                            assert result.answer, f"Should generate answer for: {query}"
                    
                    asyncio.run(test_queries())
                    
                    print("\n  ✓ Full pipeline test PASSED")
                    return True


def run_verification():
    """Run all verification tests."""
    print("=" * 70)
    print("MKDOCS RAG SYSTEM VERIFICATION")
    print("=" * 70)
    print("\nThis script verifies the system logic without external API dependencies.")
    print("All Google GenAI API calls are mocked with deterministic responses.\n")
    
    mock_genai = create_mock_genai()
    
    tests = [
        ("Markdown Parsing", lambda: test_markdown_parsing()),
        ("Vector Store", lambda: test_vector_store_operations(mock_genai)),
        ("Retriever", lambda: test_retriever(mock_genai)),
        ("Full Pipeline", lambda: test_full_pipeline(mock_genai))
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"\n  ✗ {test_name} test FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    print(f"Total Tests: {len(tests)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n✓ ALL TESTS PASSED - System verification successful!")
        print("\nThe RAG pipeline logic is working correctly.")
        print("To run with real API keys, set GOOGLE_API_KEY environment variable.")
        return 0
    else:
        print(f"\n✗ {failed} TEST(S) FAILED - Please review errors above.")
        return 1


if __name__ == "__main__":
    exit_code = run_verification()
    sys.exit(exit_code)

