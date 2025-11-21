# MkDocs RAG Demo

A demonstration project featuring a beautiful MkDocs documentation site with an embedded chat assistant powered by a custom RAG (Retrieval-Augmented Generation) pipeline using Google Gemini.

## Overview

This project showcases:
- 📚 **MkDocs Documentation Site** - Beautiful, searchable documentation with Material theme
- 💬 **Chat Assistant** - Ask questions in natural language and get answers from the docs
- 🔍 **RAG Pipeline** - Custom retrieval system using Gemini embeddings and ChromaDB
- 📎 **Source Citations** - Every answer includes cited sections from the documentation
- 🚀 **GCP Ready** - Designed for easy deployment to Google Cloud Platform

## Architecture

```
User Question → Frontend (MkDocs)
                    ↓
           Backend API (FastAPI)
                    ↓
           Query Embedding (Gemini)
                    ↓
      Vector Search (ChromaDB + pgvector)
                    ↓
           Retrieve Top-K Chunks
                    ↓
      Build Prompt + Context
                    ↓
      Gemini Generate Answer
                    ↓
      Return Answer + Citations
```

## Project Structure

```
mkdocs_rag/
├── frontend/              # MkDocs documentation site
│   ├── docs/             # Markdown documentation files
│   │   ├── index.md
│   │   ├── chat.md       # Chat interface page
│   │   ├── runbooks/     # Operational runbooks
│   │   ├── howtos/       # How-to guides
│   │   └── policies/     # Company policies
│   ├── mkdocs.yml        # MkDocs configuration
│   └── requirements.txt
│
├── backend/              # FastAPI RAG service
│   ├── rag/             # RAG pipeline components
│   │   ├── vector_store.py   # Vector storage (ChromaDB)
│   │   ├── ingestion.py      # Document chunking & embedding
│   │   ├── retriever.py      # Query & answer generation
│   │   └── models.py         # Data models
│   ├── scripts/
│   │   └── index_docs.py     # Index documentation
│   ├── tests/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration
│   └── requirements.txt
│
└── README.md
```

## Quick Start

### Prerequisites

- Python 3.10+
- Google Gemini API key ([Get one here](https://ai.google.dev/))

### 1. Clone and Setup

```bash
git clone <repository-url>
cd mkdocs_rag
```

### 2. Backend Setup

```bash
cd backend
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# Index the documentation
python -m scripts.index_docs

# Start the API server
uvicorn main:app --reload
```

The backend API will be available at http://localhost:8000

### 3. Frontend Setup

Open a new terminal:

```bash
cd frontend
pip install -r requirements.txt

# Start the MkDocs server
mkdocs serve
```

The documentation site will be available at http://localhost:8000 (or 8001 if 8000 is taken)

### 4. Try It Out!

1. Open the documentation site in your browser
2. Navigate to the "Chat Assistant" page
3. Ask questions like:
   - "How do I handle a SEV-1 incident?"
   - "What is the deployment process?"
   - "How do I request production database access?"

## Features

### Documentation Site
- Modern Material Design theme with light/dark mode
- Full-text search
- Responsive navigation
- Syntax highlighting
- Mobile-friendly

### Chat Assistant
- Natural language question answering
- Multiple AI model options (Gemini, Groq Llama, Mixtral)
- Semantic search across all documentation
- Source citations with direct links
- Context-aware responses
- Clean, intuitive interface

### RAG Pipeline
- Document chunking by headers with overlap
- Gemini text embeddings (models/embedding-001)
- ChromaDB vector storage
- Gemini 1.5 Flash for answer generation
- Configurable retrieval parameters

## Configuration

### Backend Configuration

Edit `backend/.env`:

```env
# API Keys
GOOGLE_API_KEY=your_key_here
GROQ_API_KEY=your_groq_key_here  # Optional, for Llama models

# Paths
DOCS_PATH=../frontend/docs
CHROMA_PERSIST_DIR=./chroma_db

# RAG Parameters
EMBEDDING_MODEL=models/embedding-001
GENERATION_MODEL=gemini-1.5-flash
GROQ_GENERATION_MODEL=llama-3.1-8b-instant
CHUNK_SIZE=500
CHUNK_OVERLAP=100
TOP_K_RESULTS=5
```

### Frontend Configuration

Edit `frontend/mkdocs.yml`:

```yaml
extra:
  backend_api_url: http://localhost:8000  # Change for production
```

## API Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `POST /api/chat` - Chat with documentation
  ```json
  {
    "question": "How do I deploy to production?",
    "model": "groq-llama3"  // optional, defaults to "gemini"
  }
  ```
- `GET /api/models` - Get list of available models
- `POST /api/reindex` - Rebuild vector index (see [Reindexing](#reindexing) section)
- `GET /docs` - Interactive API documentation (Swagger UI)

## Reindexing

The vector index needs to be rebuilt whenever documentation content changes. Reindexing processes all markdown files, creates embeddings, and updates the vector store.

### When to Reindex

- After adding, modifying, or deleting documentation files
- When updating the documentation structure or content
- If search results seem outdated or incomplete
- After initial setup (first-time indexing)

### How to Reindex

**Option 1: Using the API endpoint (recommended)**

```bash
curl -X POST http://localhost:8000/api/reindex
```

**Option 2: Using the indexing script**

```bash
cd backend
python -m scripts.index_docs
```

### What Happens During Reindexing

1. **Clear existing index** - Removes all existing vectors from the store
2. **Scan documentation** - Finds all `.md` files in the configured `DOCS_PATH`
3. **Parse and chunk** - Splits documents by headers with configurable overlap
4. **Generate embeddings** - Creates vector embeddings using Gemini's embedding model
5. **Store vectors** - Saves embeddings and metadata to ChromaDB

### Reindexing Response

```json
{
  "status": "success",
  "chunks_indexed": 42
}
```

### Notes

- Reindexing can take several minutes depending on the number of documents
- The API remains available during reindexing, but may return stale results until complete
- For production deployments, consider scheduling periodic reindexing or triggering it via CI/CD when docs change

## Testing

### Backend Tests

```bash
cd backend
pytest tests/
```

### Demo Questions

See `backend/tests/demo_questions.md` for a curated list of questions to demonstrate the system.

## Deployment to GCP

### Backend (Cloud Run)

```bash
# Build and push container from project root
gcloud builds submit --tag gcr.io/PROJECT_ID/mkdocs-rag-backend -f backend/Dockerfile .

# Deploy to Cloud Run
gcloud run deploy mkdocs-rag-backend \
  --image gcr.io/PROJECT_ID/mkdocs-rag-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=your_key
```

### Frontend (Firebase Hosting or Cloud Storage)

```bash
cd frontend

# Build static site
mkdocs build

# Deploy to Firebase
firebase deploy

# Or upload to Cloud Storage
gsutil -m rsync -r site/ gs://your-bucket/
```

### Environment Variables for Production

Set these in Cloud Run:
- `GOOGLE_API_KEY` - Your Gemini API key
- `DOCS_PATH` - Path to docs in container
- `GENERATION_MODEL` - Gemini model to use

## Development

### Adding New Documentation

1. Add markdown files to `frontend/docs/`
2. Update navigation in `frontend/mkdocs.yml`
3. **Reindex the vector store** to make new content searchable:
   ```bash
   curl -X POST http://localhost:8000/api/reindex
   ```
   See the [Reindexing](#reindexing) section for more details.

### Customizing the RAG Pipeline

- **Chunking Strategy**: Edit `backend/rag/ingestion.py`
- **Retrieval**: Modify `backend/rag/retriever.py`
- **Vector Store**: Swap implementation in `backend/rag/vector_store.py`

### Future: Hybrid RAG + Web Grounding

The `HybridRetriever` class in `backend/rag/retriever.py` provides an extension point for adding web-grounded search using Gemini with Google Search. This allows fallback to external sources when internal docs lack information.

## Troubleshooting

### Backend won't start
- Check `GOOGLE_API_KEY` is set in `.env`
- Verify Python dependencies installed
- Check port 8000 is available

### Chat not working
- Ensure backend is running
- Check `backend_api_url` in `mkdocs.yml`
- Check browser console for errors
- Verify CORS settings in `backend/main.py`

### No search results
- **Reindex the vector store**: `curl -X POST http://localhost:8000/api/reindex` or run `python -m scripts.index_docs`
- Check logs for embedding errors
- Verify `DOCS_PATH` points to correct location
- Ensure documents exist in the configured path

## Technology Stack

- **Frontend**: MkDocs, Material for MkDocs, Vanilla JavaScript
- **Backend**: FastAPI, Python 3.10+
- **LLM**: Google Gemini (embeddings + generation)
- **Vector Store**: ChromaDB (demo) / PostgreSQL + pgvector (production)
- **Deployment**: GCP (Cloud Run, Firebase Hosting)

## License

MIT License - feel free to use for your own projects!

## Contributing

This is a demo project, but suggestions and improvements are welcome!

## Acknowledgments

- Built with [MkDocs](https://www.mkdocs.org/) and [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- Powered by [Google Gemini](https://ai.google.dev/)
- Vector storage by [ChromaDB](https://www.trychroma.com/)
