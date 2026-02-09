from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from models.schemas import ChatRequest
from core.agent import stream_agent_events
from api.dependencies import get_agent

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/stream")
async def chat_stream(request: ChatRequest, agent=Depends(get_agent)):
    """Stream agent response as Server-Sent Events.

    Event types:
        step   - intermediate steps (thinking, sql_query, sql_result)
        answer - final agent answer
        done   - stream complete
    """
    return StreamingResponse(
        stream_agent_events(agent, request.question, request.thread_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
