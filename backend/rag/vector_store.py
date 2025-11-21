import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Optional
import logging
import os
from pathlib import Path

from config import settings
from rag.models import DocumentChunk, RetrievedChunk

logger = logging.getLogger(__name__)

os.environ["ANONYMIZED_TELEMETRY"] = "False"


class VectorStore:
    def __init__(self):
        persist_dir = Path(settings.chroma_persist_dir)
        persist_dir.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=str(persist_dir),
            settings=ChromaSettings(anonymized_telemetry=False, allow_reset=True),
        )

        try:
            collection_name = "documentation"
            try:
                self.collection = self.client.get_collection(name=collection_name)
                doc_count = self.collection.count()
                logger.info(f"Found existing collection with {doc_count} documents")
            except Exception:
                logger.info(
                    f"Collection '{collection_name}' not found, creating new one"
                )
                self.collection = self.client.create_collection(
                    name=collection_name, metadata={"hnsw:space": "cosine"}
                )
                doc_count = self.collection.count()
                logger.info(f"Created new collection with {doc_count} documents")
        except Exception as e:
            logger.error(f"Error initializing collection: {e}", exc_info=True)
            raise

    def add_chunks(self, chunks: List[DocumentChunk]):
        if not chunks:
            return

        ids = [chunk.id for chunk in chunks]
        embeddings = [chunk.embedding for chunk in chunks]
        documents = [chunk.text for chunk in chunks]
        metadatas = []

        for chunk in chunks:
            metadata = {
                "doc_path": str(chunk.doc_path),
                "title": str(chunk.title),
            }
            for key, value in chunk.metadata.items():
                if isinstance(value, (str, int, float, bool)):
                    metadata[str(key)] = value
                else:
                    metadata[str(key)] = str(value)
            metadatas.append(metadata)

        try:
            self.collection.add(
                ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas
            )
            logger.info(f"Added {len(chunks)} chunks to vector store")
        except Exception as e:
            logger.error(f"Error adding chunks to vector store: {e}")
            raise

    def search(
        self, query_embedding: List[float], top_k: int = 5
    ) -> List[RetrievedChunk]:
        if self.collection.count() == 0:
            logger.warning("Vector store is empty. No documents to search.")
            return []

        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances"],
            )

            if not results.get("ids") or not results["ids"][0]:
                logger.warning("Query returned no results")
                return []

            chunks = []
            for i, doc_id in enumerate(results["ids"][0]):
                metadata = (
                    results["metadatas"][0][i]
                    if results.get("metadatas") and results["metadatas"][0]
                    else {}
                )
                text = (
                    results["documents"][0][i]
                    if results.get("documents") and results["documents"][0]
                    else ""
                )
                distance = (
                    results["distances"][0][i]
                    if results.get("distances") and results["distances"][0]
                    else 1.0
                )

                score = max(0.0, 1.0 - distance)

                chunks.append(
                    RetrievedChunk(
                        doc_path=metadata.get("doc_path", ""),
                        title=metadata.get("title", ""),
                        text=text,
                        score=score,
                        metadata=metadata,
                    )
                )

            logger.info(f"Search returned {len(chunks)} results")
            return chunks

        except Exception as e:
            logger.error(f"Error searching vector store: {e}", exc_info=True)
            return []

    def clear(self):
        self.client.delete_collection("documentation")
        self.collection = self.client.get_or_create_collection(
            name="documentation", metadata={"hnsw:space": "cosine"}
        )
        logger.info("Vector store cleared")

    def count(self) -> int:
        return self.collection.count()
