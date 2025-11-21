from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class DocumentChunk(BaseModel):
    id: str
    doc_path: str
    title: str
    text: str
    embedding: Optional[List[float]] = None
    metadata: dict = {}


class RetrievedChunk(BaseModel):
    doc_path: str
    title: str
    text: str
    score: float
    metadata: dict = {}


class QueryResult(BaseModel):
    answer: str
    chunks: List[RetrievedChunk]
    query: str


class ChatMessage(BaseModel):
    role: str
    content: str
    sources: Optional[List[dict]] = None
    created_at: Optional[datetime] = None


class ChatSession(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime
