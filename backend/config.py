import os
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, AliasChoices

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(str(ROOT_DIR / ".env"), str(BASE_DIR / ".env")),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False
    )

    # === Database ===
    database_url: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/rag_db",
        validation_alias=AliasChoices("DATABASE_URL", "database_url")
    )
    db_pool_size: int = Field(default=10)
    db_max_overflow: int = Field(default=20)

    # === LLM API ===
    api_key: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("API_KEY", "HF_TOKEN_2", "HF_TOKEN", "api_key")
    )
    api_base_url: str = Field(
        default="https://api.sarvam.ai/v1/",
        validation_alias=AliasChoices("API_BASE_URL", "api_base_url")
    )
    llm_model: str = Field(default="sarvam-105b")
    llm_temperature: float = Field(default=0.2)
    llm_max_tokens: int = Field(default=4096)

    # === Embedding & Reranker Models ===
    embedding_model: str = Field(default="BAAI/bge-base-en-v1.5")
    reranker_model: str = Field(default="cross-encoder/ms-marco-MiniLM-L-6-v2")

    # === Chunking ===
    chunk_size: int = Field(default=1000)
    chunk_overlap: int = Field(default=200)

    # === Retrieval & Reranker Thresholds ===
    top_k: int = Field(default=5)
    initial_top_k: int = Field(default=20)
    embedding_threshold: float = Field(default=0.35)
    reranker_threshold: float = Field(default=0.25)

    # === Memory & Context Limits ===
    max_history_turns: int = Field(default=2)
    max_assistant_chars: int = Field(default=150)

    # === Document & Vector Store Paths ===
    pdf_filename: str = Field(default="netflix.pdf")
    documents_dir: str = Field(default=str(BASE_DIR / "data"))
    chroma_db_dir: str = Field(default=str(ROOT_DIR / "chroma_db"))

    # === Server & Security ===
    server_port: int = Field(default=8000)
    cors_origins: List[str] = Field(default=["http://localhost:5173"])

    @property
    def pdf_path(self) -> str:
        return str(Path(self.documents_dir) / self.pdf_filename)


# Global singleton settings instance
settings = Settings()
