from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    model_name: str = "google_genai:gemini-2.5-flash"
    db_url: str = "https://storage.googleapis.com/benchmarks-artifacts/chinook/Chinook.db"
    db_path: Path = Path("Chinook.db")
    top_k: int = 5
    cors_origins: tuple[str, ...] = ("http://localhost:3000",)
