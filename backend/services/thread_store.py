import json
import uuid
from datetime import datetime, timezone
from pathlib import Path


class ThreadStore:
    """Simple JSON-file-backed thread metadata store.

    Stores thread metadata (id, title, mode, timestamps).
    Conversation messages are stored separately in LangGraph checkpoints.
    """

    def __init__(self, file_path: str = "thread_store.json"):
        self._file = Path(file_path)
        self._threads: dict[str, dict] = {}
        self._load()

    def _load(self):
        if self._file.exists():
            try:
                self._threads = json.loads(self._file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                self._threads = {}

    def _save(self):
        self._file.write_text(
            json.dumps(self._threads, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def create(self, title: str | None = None, mode: str = "sql") -> dict:
        thread_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        thread = {
            "id": thread_id,
            "title": title or "New Chat",
            "mode": mode,
            "created_at": now,
            "updated_at": now,
        }
        self._threads[thread_id] = thread
        self._save()
        return thread

    def list_all(self) -> list[dict]:
        return sorted(
            self._threads.values(),
            key=lambda t: t["updated_at"],
            reverse=True,
        )

    def get(self, thread_id: str) -> dict | None:
        return self._threads.get(thread_id)

    def update(self, thread_id: str, **kwargs) -> dict | None:
        thread = self._threads.get(thread_id)
        if not thread:
            return None
        for key, value in kwargs.items():
            if value is not None:
                thread[key] = value
        thread["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._save()
        return thread

    def delete(self, thread_id: str) -> bool:
        if thread_id in self._threads:
            del self._threads[thread_id]
            self._save()
            return True
        return False
