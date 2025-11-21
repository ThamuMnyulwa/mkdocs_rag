from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import uuid
from typing import List, Optional
from contextlib import asynccontextmanager

from config import settings
from rag.vector_store import VectorStore
from rag.retriever import Retriever
from rag.llm_providers import LLMFactory
from rag.chat_db import ChatDatabase
from rag.models import ChatMessage

logging.basicConfig(
    level=settings.log_level.upper(),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


class TelemetryFilter(logging.Filter):
    def filter(self, record):
        return not (
            "chromadb.telemetry" in record.name
            and "Failed to send telemetry" in record.getMessage()
        )


logging.getLogger().addFilter(TelemetryFilter())

logger = logging.getLogger(__name__)

vector_store: Optional[VectorStore] = None
retriever: Optional[Retriever] = None
chat_db: Optional[ChatDatabase] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global vector_store, retriever, chat_db
    logger.info("Initializing application...")

    try:
        vector_store = VectorStore()
        retriever = Retriever(vector_store)
        chat_db = ChatDatabase()
        await chat_db.initialize()
        logger.info("Application initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise

    yield

    logger.info("Shutting down application...")


app = FastAPI(
    title="Documentation RAG API",
    description="RAG-powered API for querying documentation",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    question: str
    model: Optional[str] = None
    session_id: Optional[str] = None


class Source(BaseModel):
    doc_path: str
    title: str
    snippet: str
    score: float
    url: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    sources: List[Source]
    session_id: str


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "vector_store_initialized": vector_store is not None,
        "retriever_initialized": retriever is not None,
    }


@app.get("/api/models")
async def get_models():
    return {"models": LLMFactory.get_available_models(), "default": "gemini"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not retriever:
        raise HTTPException(status_code=503, detail="Retriever not initialized")
    if not chat_db:
        raise HTTPException(status_code=503, detail="Chat database not initialized")

    try:
        session_id = request.session_id
        if not session_id:
            session_id = str(uuid.uuid4())
            await chat_db.create_session(session_id)
            logger.info(f"Created new session: {session_id}")
        else:
            if not await chat_db.session_exists(session_id):
                await chat_db.create_session(session_id)
                logger.info(f"Created session from provided ID: {session_id}")

        conversation_history = []
        if settings.enable_chat_history:
            conversation_history = await chat_db.get_recent_messages(
                session_id, limit=settings.max_history_messages
            )
            logger.info(
                f"Processing question: {request.question} with model: {request.model or 'default'} (session: {session_id}, history: {len(conversation_history)} messages)"
            )

            if conversation_history:
                logger.debug(
                    f"History types: {[type(msg).__name__ for msg in conversation_history]}"
                )
        else:
            logger.info(
                f"Processing question: {request.question} with model: {request.model or 'default'} (session: {session_id}, history disabled)"
            )

        await chat_db.add_message(session_id, "user", request.question)

        result = await retriever.query(
            request.question,
            request.model,
            conversation_history if settings.enable_chat_history else None,
        )

        sources = [
            Source(
                doc_path=chunk.doc_path,
                title=chunk.title,
                snippet=(
                    chunk.text[:200] + "..." if len(chunk.text) > 200 else chunk.text
                ),
                score=chunk.score,
                url=f"../{chunk.doc_path.replace('.md', '/')}",
            )
            for chunk in result.chunks
        ]

        sources_dict = [
            {
                "doc_path": source.doc_path,
                "title": source.title,
                "snippet": source.snippet,
                "score": source.score,
                "url": source.url,
            }
            for source in sources
        ]

        await chat_db.add_message(session_id, "assistant", result.answer, sources_dict)

        logger.info(f"Generated answer with {len(sources)} sources")

        return ChatResponse(
            answer=result.answer, sources=sources, session_id=session_id
        )

    except Exception as e:
        logger.error(f"Error processing question: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/sessions")
async def create_session():
    if not chat_db:
        raise HTTPException(status_code=503, detail="Chat database not initialized")

    try:
        session_id = str(uuid.uuid4())
        await chat_db.create_session(session_id)
        return {"session_id": session_id}
    except Exception as e:
        logger.error(f"Error creating session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sessions/{session_id}/messages")
async def get_session_messages(session_id: str):
    if not chat_db:
        raise HTTPException(status_code=503, detail="Chat database not initialized")

    try:
        if not await chat_db.session_exists(session_id):
            raise HTTPException(status_code=404, detail="Session not found")

        messages = await chat_db.get_messages(session_id)
        return {"messages": messages}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session messages: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/reindex")
async def reindex():
    if not vector_store:
        raise HTTPException(status_code=503, detail="Vector store not initialized")

    try:
        logger.info("Starting reindexing...")
        from rag.ingestion import ingest_docs

        num_chunks = await ingest_docs(vector_store)
        logger.info(f"Reindexing complete. Indexed {num_chunks} chunks")

        return {"status": "success", "chunks_indexed": num_chunks}

    except Exception as e:
        logger.error(f"Error during reindexing: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    return {"message": "Documentation RAG API", "docs": "/docs", "health": "/health"}
