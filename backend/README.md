# Backend - FastAPI RAG Service

This directory contains the FastAPI backend that powers the documentation chat assistant using a custom RAG pipeline with Gemini.

## Setup

1. Install dependencies:
```bash
uv sync
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

3. Index the documentation:
```bash
uv run python -m scripts.index_docs
```

4. Run the development server:
```bash
uv run uvicorn main:app --reload
```

The API will be available at http://localhost:8000

## API Endpoints

- `GET /health` - Health check
- `POST /api/chat` - Chat with documentation
- `POST /api/reindex` - Rebuild the vector index (see [Reindexing](#reindexing) below)
- `GET /docs` - Interactive API documentation (Swagger UI)

## Reindexing

The `/api/reindex` endpoint rebuilds the vector index from all markdown files in the documentation directory. This is necessary whenever documentation content changes.

**When to reindex:**
- After adding, modifying, or deleting documentation files
- When search results seem outdated
- After initial setup

**How to use:**
```bash
curl -X POST http://localhost:8000/api/reindex
```

The endpoint returns:
```json
{
  "status": "success",
  "chunks_indexed": 42
}
```

**What it does:**
1. Clears the existing vector store
2. Scans all `.md` files in `DOCS_PATH`
3. Parses and chunks documents by headers
4. Generates embeddings using Gemini
5. Stores vectors in ChromaDB

**Note:** Reindexing can take several minutes depending on document count. The API remains available during reindexing.

## Architecture

- `main.py` - FastAPI application and endpoints
- `config.py` - Configuration management
- `rag/` - RAG pipeline components
  - `vector_store.py` - Vector storage abstraction (ChromaDB)
  - `ingestion.py` - Document parsing, chunking, and indexing
  - `retriever.py` - Query processing and answer generation
  - `models.py` - Data models

## Environment Variables

See `.env.example` for all available configuration options.

Key variables:
- `GOOGLE_API_KEY` - Your Gemini API key (required)
- `GROQ_API_KEY` - Your Groq API key (optional, for Llama models)
- `DOCS_PATH` - Path to the MkDocs documentation folder
- `EMBEDDING_MODEL` - Gemini embedding model to use
- `GENERATION_MODEL` - Gemini text generation model to use
- `GROQ_GENERATION_MODEL` - Groq model to use (default: llama-3.1-8b-instant)

## GCP Deployment

The backend can be deployed to:
- Cloud Run (recommended for serverless)
- Compute Engine
- GKE (for larger scale)

See the main README for deployment instructions.

