import os
from dataclasses import dataclass, field
# from pathlib import Path


def _cors_origins() -> tuple[str, ...]:
    raw = os.getenv("CORS_ORIGINS", "http://localhost:3000")
    return tuple(o.strip() for o in raw.split(",") if o.strip())


@dataclass(frozen=True)
class Settings:
    # LLM
    model_name: str = field(
        default_factory=lambda: os.getenv("MODEL_NAME", "google_genai:gemini-2.5-flash")
    )

    # SQLlite Database
    # db_url: str = field(
    #     default_factory=lambda: os.getenv(
    #         "DATABASE_URL",
    #         "https://storage.googleapis.com/benchmarks-artifacts/chinook/Chinook.db",
    #     )
    # )
    # db_path: Path = field(
    #     default_factory=lambda: Path(os.getenv("DATABASE_PATH", "Chinook.db"))
    # )

    # SQL Server Database
    db_url: str = field(
        default_factory=lambda: os.getenv(
            "DATABASE_URL",
        )
    )
    top_k: int = field(default_factory=lambda: int(os.getenv("TOP_K", "5")))

    # CORS
    cors_origins: tuple[str, ...] = field(default_factory=_cors_origins)

    # ChromaDB
    chroma_host: str = field(
        default_factory=lambda: os.getenv("CHROMA_HOST", "localhost")
    )
    chroma_port: int = field(
        default_factory=lambda: int(os.getenv("CHROMA_PORT", "8100"))
    )

    # Document upload
    upload_dir: str = field(
        default_factory=lambda: os.getenv("UPLOAD_DIR", "./uploads")
    )
    max_file_size_mb: int = field(
        default_factory=lambda: int(os.getenv("MAX_FILE_SIZE_MB", "50"))
    )
    allowed_file_types: tuple[str, ...] = ("pdf", "csv", "txt", "docx")

    # Embeddings
    embedding_model: str = field(
        default_factory=lambda: os.getenv(
            "EMBEDDING_MODEL", "models/gemini-embedding-001"
        )
    )

    # Server
    host: str = field(default_factory=lambda: os.getenv("HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: int(os.getenv("PORT", "8000")))
