import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.app import build_app
from core.settings import Settings
from services.thread_store import ThreadStore
from services.document_store import DocumentStore
from api.routes import chat, threads, database, documents
from pathlib import Path
from dotenv import load_dotenv
import uvicorn

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize application state on startup."""
    components = build_app()
    app.state.agents = components["agents"]
    app.state.db = components["db"]
    app.state.vectorstore = components["vectorstore"]
    app.state.settings = components["settings"]
    app.state.thread_store = ThreadStore()
    app.state.document_store = DocumentStore()
    yield


# Settings are loaded after dotenv in build_app, but we need them for
# middleware setup too. load_dotenv here so Settings() picks up .env values.


env_path = Path(".env") if Path(".env").exists() else Path("../.env")
load_dotenv(env_path)
_settings = Settings()

app = FastAPI(
    title="SQL Agent API",
    description="AI-powered SQL database and document assistant",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(_settings.cors_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(threads.router)
app.include_router(database.router)
app.include_router(documents.router)


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", host=_settings.host, port=_settings.port, reload=True)
