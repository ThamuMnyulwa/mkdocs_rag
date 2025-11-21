import os
import re
import hashlib
from pathlib import Path
from typing import List
import logging
import frontmatter
import google.generativeai as genai

from config import settings
from rag.models import DocumentChunk
from rag.vector_store import VectorStore

logger = logging.getLogger(__name__)

genai.configure(api_key=settings.google_api_key)


def parse_markdown_file(file_path: Path) -> tuple[str, str, str]:
    with open(file_path, 'r', encoding='utf-8') as f:
        post = frontmatter.load(f)
        content = post.content
        title = post.get('title', file_path.stem.replace('-', ' ').title())
    
    relative_path = file_path.relative_to(settings.docs_path_absolute)
    
    return str(relative_path), title, content


def clean_markdown(text: str) -> str:
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    text = re.sub(r'```[^\n]*\n.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    text = re.sub(r'#+\s+', '', text)
    text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^\*]+)\*', r'\1', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()


def chunk_by_headers(content: str, doc_path: str, title: str) -> List[DocumentChunk]:
    chunks = []
    
    sections = re.split(r'\n(#{1,3}\s+.+)\n', content)
    
    if len(sections) == 1:
        chunk_text = clean_markdown(content)
        if chunk_text:
            chunk_id = hashlib.md5(f"{doc_path}:0".encode()).hexdigest()
            chunks.append(DocumentChunk(
                id=chunk_id,
                doc_path=doc_path,
                title=title,
                text=chunk_text,
                metadata={"section": title}
            ))
        return chunks
    
    current_text = sections[0]
    
    for i in range(1, len(sections), 2):
        if i + 1 < len(sections):
            header = sections[i].strip()
            section_content = sections[i + 1]
            
            if current_text.strip():
                chunk_text = clean_markdown(current_text)
                if chunk_text and len(chunk_text) > 50:
                    chunk_id = hashlib.md5(f"{doc_path}:{len(chunks)}".encode()).hexdigest()
                    chunks.append(DocumentChunk(
                        id=chunk_id,
                        doc_path=doc_path,
                        title=title,
                        text=chunk_text,
                        metadata={"section": title}
                    ))
            
            section_title = re.sub(r'^#+\s+', '', header)
            combined_text = f"{section_title}\n\n{section_content}"
            chunk_text = clean_markdown(combined_text)
            
            if len(chunk_text) > settings.chunk_size:
                sub_chunks = chunk_by_size(chunk_text, settings.chunk_size, settings.chunk_overlap)
                for j, sub_chunk in enumerate(sub_chunks):
                    chunk_id = hashlib.md5(f"{doc_path}:{len(chunks)}:{j}".encode()).hexdigest()
                    chunks.append(DocumentChunk(
                        id=chunk_id,
                        doc_path=doc_path,
                        title=f"{title} - {section_title}",
                        text=sub_chunk,
                        metadata={"section": section_title}
                    ))
            elif chunk_text and len(chunk_text) > 50:
                chunk_id = hashlib.md5(f"{doc_path}:{len(chunks)}".encode()).hexdigest()
                chunks.append(DocumentChunk(
                    id=chunk_id,
                    doc_path=doc_path,
                    title=f"{title} - {section_title}",
                    text=chunk_text,
                    metadata={"section": section_title}
                ))
            
            current_text = ""
        else:
            current_text += sections[i]
    
    if current_text.strip():
        chunk_text = clean_markdown(current_text)
        if chunk_text and len(chunk_text) > 50:
            chunk_id = hashlib.md5(f"{doc_path}:{len(chunks)}".encode()).hexdigest()
            chunks.append(DocumentChunk(
                id=chunk_id,
                doc_path=doc_path,
                title=title,
                text=chunk_text,
                metadata={"section": "Additional Content"}
            ))
    
    return chunks


def chunk_by_size(text: str, size: int, overlap: int) -> List[str]:
    chunks = []
    words = text.split()
    
    start = 0
    while start < len(words):
        end = start + size
        chunk = ' '.join(words[start:end])
        chunks.append(chunk)
        
        if end >= len(words):
            break
        
        start = end - overlap
    
    return chunks


def embed_chunks(chunks: List[DocumentChunk]) -> List[DocumentChunk]:
    logger.info(f"Embedding {len(chunks)} chunks...")
    
    for i, chunk in enumerate(chunks):
        try:
            result = genai.embed_content(
                model=settings.embedding_model,
                content=chunk.text,
                task_type="retrieval_document"
            )
            chunk.embedding = result['embedding']
            
            if (i + 1) % 10 == 0:
                logger.info(f"Embedded {i + 1}/{len(chunks)} chunks")
                
        except Exception as e:
            logger.error(f"Error embedding chunk {chunk.id}: {e}")
            raise
    
    logger.info(f"Successfully embedded all {len(chunks)} chunks")
    return chunks


async def ingest_docs(vector_store: VectorStore) -> int:
    logger.info("Starting document ingestion...")
    
    vector_store.clear()
    
    docs_path = settings.docs_path_absolute
    if not docs_path.exists():
        raise ValueError(f"Documentation path does not exist: {docs_path}")
    
    all_chunks = []
    
    md_files = list(docs_path.rglob("*.md"))
    logger.info(f"Found {len(md_files)} markdown files")
    
    for md_file in md_files:
        if md_file.name.startswith('.') or 'node_modules' in str(md_file):
            continue
        
        try:
            doc_path, title, content = parse_markdown_file(md_file)
            logger.info(f"Processing: {doc_path}")
            
            chunks = chunk_by_headers(content, doc_path, title)
            all_chunks.extend(chunks)
            
            logger.info(f"  Created {len(chunks)} chunks from {doc_path}")
            
        except Exception as e:
            logger.error(f"Error processing {md_file}: {e}")
            continue
    
    if not all_chunks:
        logger.warning("No chunks created from documents")
        return 0
    
    logger.info(f"Total chunks created: {len(all_chunks)}")
    
    all_chunks = embed_chunks(all_chunks)
    
    vector_store.add_chunks(all_chunks)
    
    logger.info(f"Ingestion complete. Total chunks in store: {vector_store.count()}")
    
    return len(all_chunks)

