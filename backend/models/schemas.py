from pydantic import BaseModel
from typing import Literal


class ChatRequest(BaseModel):
    thread_id: str
    question: str
    mode: Literal["sql", "rag", "hybrid"] | None = None


class ThreadCreate(BaseModel):
    title: str | None = None
    mode: str = "sql"


class ThreadUpdate(BaseModel):
    title: str | None = None


class ThreadResponse(BaseModel):
    id: str
    title: str
    mode: str
    created_at: str
    updated_at: str


class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    sql_query: str | None = None
    sql_result: str | None = None
    created_at: str


class ThreadDetailResponse(ThreadResponse):
    messages: list[MessageResponse] = []


class DatabaseSchemaResponse(BaseModel):
    tables: list[dict]


class TablePreviewResponse(BaseModel):
    table_name: str
    result: str


# --- Document schemas ---

class DocumentResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    file_size: int
    status: str
    chunk_count: int
    error_message: str | None = None
    created_at: str
