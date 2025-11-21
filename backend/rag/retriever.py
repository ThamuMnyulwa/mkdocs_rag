import logging
from typing import List, Optional
import google.generativeai as genai

from config import settings
from rag.models import QueryResult, RetrievedChunk
from rag.vector_store import VectorStore
from rag.llm_providers import LLMFactory

logger = logging.getLogger(__name__)

genai.configure(api_key=settings.google_api_key)


class Retriever:
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store

    async def query(
        self,
        question: str,
        model_key: Optional[str] = None,
        conversation_history: Optional[List] = None,
    ) -> QueryResult:
        logger.info(
            f"Processing query: {question} with model: {model_key or 'default'}"
        )

        query_embedding = self._embed_query(question)

        retrieved_chunks = self.vector_store.search(
            query_embedding=query_embedding, top_k=settings.top_k_results
        )

        if not retrieved_chunks:
            return QueryResult(
                answer="I couldn't find any relevant information in the documentation to answer your question.",
                chunks=[],
                query=question,
            )

        logger.info(f"Retrieved {len(retrieved_chunks)} relevant chunks")

        answer = self._generate_answer(
            question, retrieved_chunks, model_key, conversation_history
        )

        return QueryResult(answer=answer, chunks=retrieved_chunks, query=question)

    def _embed_query(self, query: str) -> List[float]:
        try:
            result = genai.embed_content(
                model=settings.embedding_model,
                content=query,
                task_type="retrieval_query",
            )
            return result["embedding"]
        except Exception as e:
            logger.error(f"Error embedding query: {e}")
            raise

    def _generate_answer(
        self,
        question: str,
        chunks: List[RetrievedChunk],
        model_key: Optional[str] = None,
        conversation_history: Optional[List] = None,
    ) -> str:
        context = self._build_context(chunks)
        prompt = self._build_prompt(question, context, chunks, conversation_history)

        try:
            provider = LLMFactory.create_provider(model_key)
            answer = provider.generate(prompt)

            logger.info(
                f"Successfully generated answer using {provider.__class__.__name__}"
            )
            return answer

        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            raise

    def _build_context(self, chunks: List[RetrievedChunk]) -> str:
        context_parts = []

        for i, chunk in enumerate(chunks, 1):
            context_parts.append(f"[Source {i}: {chunk.title}]")
            context_parts.append(chunk.text)
            context_parts.append("")

        return "\n".join(context_parts)

    def _build_prompt(
        self,
        question: str,
        context: str,
        chunks: List[RetrievedChunk],
        conversation_history: Optional[List] = None,
    ) -> str:
        source_list = "\n".join(
            [f"- {chunk.title} (from {chunk.doc_path})" for chunk in chunks]
        )

        history_text = ""
        if conversation_history and len(conversation_history) > 0:
            try:
                history_parts = []
                for msg in conversation_history:
                    if hasattr(msg, "role") and hasattr(msg, "content"):
                        if msg.role == "user":
                            content = (
                                msg.content[:500]
                                if len(msg.content) > 500
                                else msg.content
                            )
                            history_parts.append(f"Q: {content}")
                        elif msg.role == "assistant":
                            content = (
                                msg.content[:500]
                                if len(msg.content) > 500
                                else msg.content
                            )
                            history_parts.append(f"A: {content}")

                if history_parts:
                    history_text = (
                        "\n\nPREVIOUS CONVERSATION:\n" + "\n".join(history_parts) + "\n"
                    )
                    logger.info(
                        f"Including {len(history_parts)} previous messages in prompt"
                    )
            except Exception as e:
                logger.error(f"Error building conversation history: {e}", exc_info=True)
                history_text = ""

        prompt = f"""You are a helpful documentation assistant. Your job is to answer questions based on the provided documentation context.

IMPORTANT INSTRUCTIONS:
1. Use the previous conversation to understand context and what the user is referring to
2. When the user asks about previous messages (e.g., "What did I say?"), you CAN refer to the conversation history
3. For questions about the documentation content, answer using information from the provided documentation context
4. You MUST cite which documentation sources you used in your answer (reference by document title)
5. If the documentation doesn't contain enough information to answer a question about documentation, say so clearly
6. Be concise but thorough
7. Use a professional and helpful tone
8. Format your answer clearly with bullet points or paragraphs as appropriate
{history_text}
CONTEXT FROM DOCUMENTATION:
{context}

AVAILABLE SOURCES:
{source_list}

CURRENT QUESTION: {question}

ANSWER (cite documentation sources when using them):"""

        return prompt


class HybridRetriever(Retriever):
    """
    Extended retriever that can fall back to web grounding.
    This is a placeholder for future Phase 8 implementation.
    """

    def __init__(self, vector_store: VectorStore, use_web_grounding: bool = False):
        super().__init__(vector_store)
        self.use_web_grounding = use_web_grounding

    async def query(
        self,
        question: str,
        model_key: Optional[str] = None,
        conversation_history: Optional[List] = None,
    ) -> QueryResult:
        result = await super().query(question, model_key, conversation_history)

        if self.use_web_grounding and len(result.chunks) < 2:
            logger.info(
                "Low confidence in internal docs, web grounding could be used here"
            )

        return result
