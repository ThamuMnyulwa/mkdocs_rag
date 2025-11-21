import aiosqlite
import json
import uuid
import logging
from typing import List, Optional
from datetime import datetime
from pathlib import Path

from config import settings
from rag.models import ChatMessage, ChatSession

logger = logging.getLogger(__name__)


class ChatDatabase:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or settings.chat_db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    async def initialize(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    id TEXT PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    sources_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
                )
                """
            )
            await db.commit()
            logger.info(f"Chat database initialized at {self.db_path}")

    async def create_session(self, session_id: str = None) -> str:
        if not session_id:
            session_id = str(uuid.uuid4())

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO chat_sessions (id, created_at, updated_at)
                VALUES (?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """,
                (session_id,),
            )
            await db.commit()
            logger.info(f"Created chat session: {session_id}")

        return session_id

    async def session_exists(self, session_id: str) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT 1 FROM chat_sessions WHERE id = ?", (session_id,)
            )
            result = await cursor.fetchone()
            return result is not None

    async def update_session_timestamp(self, session_id: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                UPDATE chat_sessions
                SET updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (session_id,),
            )
            await db.commit()

    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        sources: Optional[List[dict]] = None,
    ) -> int:
        sources_json = json.dumps(sources) if sources else None

        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                INSERT INTO chat_messages (session_id, role, content, sources_json, created_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                """,
                (session_id, role, content, sources_json),
            )
            await db.commit()
            message_id = cursor.lastrowid
            logger.info(f"Added message {message_id} to session {session_id}")

        await self.update_session_timestamp(session_id)
        return message_id

    async def get_messages(
        self, session_id: str, limit: Optional[int] = None
    ) -> List[ChatMessage]:
        query = """
            SELECT role, content, sources_json, created_at
            FROM chat_messages
            WHERE session_id = ?
            ORDER BY created_at ASC
        """

        if limit:
            query += f" LIMIT {limit}"

        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(query, (session_id,))
            rows = await cursor.fetchall()

        messages = []
        for row in rows:
            sources = json.loads(row["sources_json"]) if row["sources_json"] else None
            messages.append(
                ChatMessage(
                    role=row["role"],
                    content=row["content"],
                    sources=sources,
                    created_at=datetime.fromisoformat(row["created_at"]),
                )
            )

        return messages

    async def get_recent_messages(
        self, session_id: str, limit: int = 10
    ) -> List[ChatMessage]:
        query = """
            SELECT role, content, sources_json, created_at
            FROM chat_messages
            WHERE session_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        """

        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(query, (session_id, limit))
            rows = await cursor.fetchall()

        messages = []
        for row in reversed(rows):
            sources = json.loads(row["sources_json"]) if row["sources_json"] else None
            messages.append(
                ChatMessage(
                    role=row["role"],
                    content=row["content"],
                    sources=sources,
                    created_at=datetime.fromisoformat(row["created_at"]),
                )
            )

        return messages

    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT id, created_at, updated_at
                FROM chat_sessions
                WHERE id = ?
                """,
                (session_id,),
            )
            row = await cursor.fetchone()

        if row:
            return ChatSession(
                id=row["id"],
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
            )
        return None

    async def delete_session(self, session_id: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "DELETE FROM chat_messages WHERE session_id = ?", (session_id,)
            )
            await db.execute("DELETE FROM chat_sessions WHERE id = ?", (session_id,))
            await db.commit()
            logger.info(f"Deleted chat session: {session_id}")
