from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.app import build_app
from services.thread_store import ThreadStore
from api.routes import chat, threads, database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize application state on startup."""
    agent, db, settings = build_app()
    app.state.agent = agent
    app.state.db = db
    app.state.settings = settings
    app.state.thread_store = ThreadStore()
    yield


app = FastAPI(
    title="SQL Agent API",
    description="AI-powered SQL database assistant",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(threads.router)
app.include_router(database.router)


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
