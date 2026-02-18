import logging
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from models.schemas import ChatRequest
from core.agent import stream_agent_events, get_agent_for_mode
from core.intent_classifier import classify_intent
from api.dependencies import get_agents, get_model

router = APIRouter(prefix="/chat", tags=["chat"])
logger = logging.getLogger("chat")


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    agents=Depends(get_agents),
    model=Depends(get_model)
):
    """Stream agent response as Server-Sent Events.

    Routes to the correct agent based on request.mode (sql, rag, hybrid).
    If mode is not specified, uses LLM-based intent classification.

    Event types:
        step   - intermediate steps (thinking, sql_query, sql_result, source)
        answer - final agent answer
        done   - stream complete
    """
    # Auto-classify if mode not specified
    mode = request.mode
    if mode is None:
        mode = classify_intent(request.question, model)
        logger.info(f"Auto-classified as '{mode}' for question: '{request.question[:50]}...'")
    
    agent = get_agent_for_mode(mode, agents)

    return StreamingResponse(
        stream_agent_events(agent, request.question, request.thread_id, mode),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
