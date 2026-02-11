from fastapi import Request


def get_agents(request: Request) -> dict:
    """Return the dict of all agents (sql, rag, hybrid)."""
    return request.app.state.agents


def get_agent(request: Request):
    """Return the SQL agent (backward compatibility)."""
    return request.app.state.agents["sql"]


def get_db(request: Request):
    return request.app.state.db


def get_vectorstore(request: Request):
    return request.app.state.vectorstore


def get_settings(request: Request):
    return request.app.state.settings


def get_thread_store(request: Request):
    return request.app.state.thread_store


def get_document_store(request: Request):
    return request.app.state.document_store
