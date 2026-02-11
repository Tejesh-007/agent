import json
import uuid
from datetime import datetime, timezone
from pathlib import Path


class DocumentStore:
    """Simple JSON-file-backed document metadata store.

    Tracks uploaded documents: id, filename, file_type, file_size,
    file_path, status, chunk_count, error_message, created_at.
    """

    def __init__(self, file_path: str = "document_store.json"):
        self._file = Path(file_path)
        self._docs: dict[str, dict] = {}
        self._load()

    def _load(self):
        if self._file.exists():
            try:
                self._docs = json.loads(self._file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                self._docs = {}

    def _save(self):
        self._file.write_text(
            json.dumps(self._docs, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def create(
        self,
        filename: str,
        file_type: str,
        file_size: int,
        file_path: str,
    ) -> dict:
        doc_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        doc = {
            "id": doc_id,
            "filename": filename,
            "file_type": file_type,
            "file_size": file_size,
            "file_path": file_path,
            "status": "processing",
            "chunk_count": 0,
            "error_message": None,
            "created_at": now,
        }
        self._docs[doc_id] = doc
        self._save()
        return doc

    def list_all(self) -> list[dict]:
        return sorted(
            self._docs.values(),
            key=lambda d: d["created_at"],
            reverse=True,
        )

    def get(self, doc_id: str) -> dict | None:
        return self._docs.get(doc_id)

    def update(self, doc_id: str, **kwargs) -> dict | None:
        doc = self._docs.get(doc_id)
        if not doc:
            return None
        for key, value in kwargs.items():
            if value is not None:
                doc[key] = value
        self._save()
        return doc

    def delete(self, doc_id: str) -> bool:
        if doc_id in self._docs:
            del self._docs[doc_id]
            self._save()
            return True
        return False
