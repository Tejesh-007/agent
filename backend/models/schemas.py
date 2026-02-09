from pydantic import BaseModel


class ChatRequest(BaseModel):
    thread_id: str
    question: str
    mode: str = "sql"


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
