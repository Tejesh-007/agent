from fastapi import APIRouter, Depends, HTTPException

from models.schemas import (
    ThreadCreate,
    ThreadUpdate,
    ThreadResponse,
    ThreadDetailResponse,
    MessageResponse,
)
from api.dependencies import get_agent, get_thread_store
from core.agent import _extract_text

router = APIRouter(prefix="/threads", tags=["threads"])


@router.get("", response_model=list[ThreadResponse])
async def list_threads(store=Depends(get_thread_store)):
    return store.list_all()


@router.post("", response_model=ThreadResponse, status_code=201)
async def create_thread(body: ThreadCreate, store=Depends(get_thread_store)):
    return store.create(title=body.title, mode=body.mode)


@router.get("/{thread_id}", response_model=ThreadDetailResponse)
async def get_thread(
    thread_id: str,
    store=Depends(get_thread_store),
    agent=Depends(get_agent),
):
    thread = store.get(thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    # Retrieve messages from LangGraph checkpoint
    messages = []
    try:
        state = agent.get_state(
            config={"configurable": {"thread_id": thread_id}}
        )
        if state and state.values:
            for msg in state.values.get("messages", []):
                msg_type = type(msg).__name__

                # Map message type to role
                if msg_type == "HumanMessage":
                    role = "user"
                elif msg_type == "AIMessage":
                    role = "assistant"
                else:
                    continue  # Skip ToolMessages

                content = _extract_text(msg)

                # Skip AI messages that are only tool calls with no text
                if (
                    msg_type == "AIMessage"
                    and getattr(msg, "tool_calls", None)
                    and not content
                ):
                    continue

                messages.append(
                    MessageResponse(
                        id=getattr(msg, "id", "") or "",
                        role=role,
                        content=content,
                        created_at=thread["created_at"],
                    )
                )
    except Exception:
        pass  # Thread may have no messages yet

    return ThreadDetailResponse(**thread, messages=messages)


@router.patch("/{thread_id}", response_model=ThreadResponse)
async def update_thread(
    thread_id: str,
    body: ThreadUpdate,
    store=Depends(get_thread_store),
):
    thread = store.update(thread_id, title=body.title)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    return thread


@router.delete("/{thread_id}", status_code=204)
async def delete_thread(thread_id: str, store=Depends(get_thread_store)):
    if not store.delete(thread_id):
        raise HTTPException(status_code=404, detail="Thread not found")
