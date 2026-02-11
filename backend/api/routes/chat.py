from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from models.schemas import ChatRequest
from core.agent import stream_agent_events, get_agent_for_mode
from api.dependencies import get_agents

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/stream")
async def chat_stream(request: ChatRequest, agents=Depends(get_agents)):
    """Stream agent response as Server-Sent Events.

    Routes to the correct agent based on request.mode (sql, rag, hybrid).

    Event types:
        step   - intermediate steps (thinking, sql_query, sql_result, source)
        answer - final agent answer
        done   - stream complete
    """
    agent = get_agent_for_mode(request.mode, agents)

    return StreamingResponse(
        stream_agent_events(agent, request.question, request.thread_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
