from pathlib import Path
import requests
from langchain_community.utilities import SQLDatabase


def ensure_database_file(url: str, path: Path) -> Path:
    if path.exists():
        return path
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    path.write_bytes(response.content)
    return path


def get_database(url: str, path: Path) -> SQLDatabase:
    resolved = ensure_database_file(url, Path(path).resolve())
    return SQLDatabase.from_uri(f"sqlite:///{resolved.as_posix()}")
