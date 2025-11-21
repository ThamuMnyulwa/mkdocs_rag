#!/usr/bin/env python3
"""
Script to index documentation into the vector store.
Run this before starting the API server for the first time.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from rag.vector_store import VectorStore
from rag.ingestion import ingest_docs
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def main():
    logger.info("Starting documentation indexing...")
    
    try:
        vector_store = VectorStore()
        num_chunks = await ingest_docs(vector_store)
        
        logger.info(f"✅ Indexing complete! Indexed {num_chunks} chunks.")
        logger.info(f"Total documents in store: {vector_store.count()}")
        
    except Exception as e:
        logger.error(f"❌ Indexing failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

