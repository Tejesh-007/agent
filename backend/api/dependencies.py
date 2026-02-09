from fastapi import Request


def get_agent(request: Request):
    return request.app.state.agent


def get_db(request: Request):
    return request.app.state.db


def get_settings(request: Request):
    return request.app.state.settings


def get_thread_store(request: Request):
    return request.app.state.thread_store
