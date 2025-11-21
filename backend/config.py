from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    google_api_key: str
    groq_api_key: str = ""
    docs_path: str = "../frontend/docs"  # Path to the MkDocs documentation folder
    chroma_persist_dir: str = "./chroma_db"  # Path to the ChromaDB database folder
    chat_db_path: str = "./chat_history.db"  # Path to the chat history database folder

    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "info"

    embedding_model: str = "models/embedding-001"
    generation_model: str = "gemini-2.5-flash"
    groq_generation_model: str = "llama-3.1-8b-instant"
    chunk_size: int = 500
    chunk_overlap: int = 100
    top_k_results: int = 5
    max_history_messages: int = 10
    enable_chat_history: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def docs_path_absolute(self) -> Path:
        return Path(self.docs_path).resolve()


settings = Settings()
