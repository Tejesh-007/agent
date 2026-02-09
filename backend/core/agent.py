import json

from langchain.agents import create_agent
from langchain_community.agent_toolkits import SQLDatabaseToolkit

from core.prompts import build_system_prompt


def create_sql_agent(model, db, top_k: int = 5, checkpointer=None):
    """Create a LangGraph SQL agent with optional thread memory."""
    toolkit = SQLDatabaseToolkit(db=db, llm=model)
    tools = toolkit.get_tools()
    system_prompt = build_system_prompt(db.dialect, top_k)
    return create_agent(
        model,
        tools,
        system_prompt=system_prompt,
        checkpointer=checkpointer,
    )


def _extract_text(value) -> str:
    """Extract plain text from various LangChain message formats."""
    if value is None:
        return ""
    if hasattr(value, "content"):
        value = value.content
    if isinstance(value, dict) and "text" in value:
        return str(value["text"]).strip()
    if isinstance(value, list):
        parts = []
        for item in value:
            if hasattr(item, "content"):
                parts.append(str(item.content))
            elif isinstance(item, dict) and "text" in item:
                parts.append(str(item["text"]))
            else:
                parts.append(str(item))
        return "".join(parts).strip()
    return str(value).strip()


def run_agent(agent, question: str, thread_id: str | None = None) -> str:
    """Run the agent synchronously and return the final text answer."""
    config = {}
    if thread_id:
        config = {"configurable": {"thread_id": thread_id}}
    response = None
    for step in agent.stream(
        {"messages": [{"role": "user", "content": question}]},
        config=config,
        stream_mode="values",
    ):
        response = step["messages"][-1]
    return _extract_text(response)


def stream_agent_events(agent, question: str, thread_id: str):
    """Generator that yields SSE-formatted events from agent execution.

    Event types:
        step  - intermediate reasoning (thinking, sql_query, sql_result)
        answer - final agent response
        done  - stream complete signal
    """
    config = {"configurable": {"thread_id": thread_id}}
    prev_count = 0

    for step in agent.stream(
        {"messages": [{"role": "user", "content": question}]},
        config=config,
        stream_mode="values",
    ):
        messages = step["messages"]
        new_messages = messages[prev_count:]
        prev_count = len(messages)

        for msg in new_messages:
            msg_type = type(msg).__name__

            if msg_type == "HumanMessage":
                continue

            if msg_type == "AIMessage":
                tool_calls = getattr(msg, "tool_calls", None)
                if tool_calls:
                    for tc in tool_calls:
                        tool_name = tc.get("name", "")
                        tool_args = tc.get("args", {})

                        if tool_name == "sql_db_query":
                            query = tool_args.get("query", "")
                            yield _sse_event(
                                "step",
                                {"type": "sql_query", "content": query},
                            )
                        else:
                            yield _sse_event(
                                "step",
                                {
                                    "type": "thinking",
                                    "content": f"Using tool: {tool_name}",
                                },
                            )
                else:
                    content = _extract_text(msg)
                    if content:
                        yield _sse_event(
                            "answer",
                            {"type": "final", "content": content},
                        )

            elif msg_type == "ToolMessage":
                tool_name = getattr(msg, "name", "")
                content = _extract_text(msg)

                if tool_name == "sql_db_query":
                    yield _sse_event(
                        "step",
                        {"type": "sql_result", "content": content},
                    )
                else:
                    yield _sse_event(
                        "step",
                        {"type": "thinking", "content": content},
                    )

    yield _sse_event("done", {"status": "complete"})


def _sse_event(event: str, data: dict) -> str:
    """Format a Server-Sent Event string."""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"
