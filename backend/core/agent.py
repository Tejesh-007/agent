import json
import logging

from langchain.agents import create_agent
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.tools import tool

from core.prompts import build_system_prompt
from core.token_tracker import TokenTracker

logger = logging.getLogger("token_tracker")


# ---------------------------------------------------------------------------
# SQL Agent (existing)
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# RAG Agent
# ---------------------------------------------------------------------------


def _build_retriever_tool(vectorstore):
    """Build a retriever tool that searches the ChromaDB vectorstore."""

    @tool(response_format="content_and_artifact")
    def retrieve_context(query: str):
        """Retrieve relevant document chunks to help answer a question.

        Use this tool whenever the user asks about uploaded documents.
        The tool returns text excerpts from documents that were uploaded
        to the system.
        """
        retrieved_docs = vectorstore.similarity_search(query, k=3)
        serialized = "\n\n".join(
            f"Source: {doc.metadata.get('filename', 'unknown')} "
            f"(page {doc.metadata.get('page', '?')}, "
            f"chunk {doc.metadata.get('chunk_index', '?')})\n"
            f"Content: {doc.page_content}"
            for doc in retrieved_docs
        )
        return serialized, retrieved_docs

    return retrieve_context


RAG_SYSTEM_PROMPT = """You are a helpful assistant that answers questions based on uploaded documents.

You have access to a retrieval tool that searches through uploaded documents.
ALWAYS use the retrieve_context tool to find relevant information before answering.

When answering:
- Cite which document and page/section the information came from.
- If the retrieved context doesn't contain enough information to answer,
  say so clearly.
- Be concise and accurate.
"""


def create_rag_agent(model, vectorstore, checkpointer=None):
    """Create a RAG agent that retrieves from uploaded documents."""
    retriever_tool = _build_retriever_tool(vectorstore)
    return create_agent(
        model,
        [retriever_tool],
        system_prompt=RAG_SYSTEM_PROMPT,
        checkpointer=checkpointer,
    )


# ---------------------------------------------------------------------------
# Hybrid Agent (SQL + RAG)
# ---------------------------------------------------------------------------

HYBRID_SYSTEM_PROMPT = """You are a powerful assistant that can answer questions using BOTH:
1. A SQL database (use the sql_db_* tools to query structured data)
2. Uploaded documents (use the retrieve_context tool to search document content)

Decide which source is most appropriate based on the question:
- For questions about structured data, tables, counts, aggregations → use SQL tools
- For questions about document content, policies, reports → use retrieve_context
- For questions that need both → use both sources and combine the information

When using SQL:
- Always check available tables first with sql_db_list_tables
- Then check schema with sql_db_schema before writing queries
- NEVER execute DML statements (INSERT, UPDATE, DELETE, DROP)

When citing document sources, mention the filename and page/section.
"""


def create_hybrid_agent(model, db, vectorstore, top_k: int = 5, checkpointer=None):
    """Create a hybrid agent with both SQL and RAG tools."""
    sql_toolkit = SQLDatabaseToolkit(db=db, llm=model)
    sql_tools = sql_toolkit.get_tools()
    retriever_tool = _build_retriever_tool(vectorstore)

    all_tools = sql_tools + [retriever_tool]

    return create_agent(
        model,
        all_tools,
        system_prompt=HYBRID_SYSTEM_PROMPT,
        checkpointer=checkpointer,
    )


# ---------------------------------------------------------------------------
# Agent router
# ---------------------------------------------------------------------------


def get_agent_for_mode(mode: str, agents: dict):
    """Return the appropriate agent for the given mode.

    Args:
        mode: One of "sql", "rag", "hybrid".
        agents: Dict with keys "sql", "rag", "hybrid" mapping to agent instances.

    Returns:
        The agent for the requested mode.
    """
    if mode not in agents:
        raise ValueError(f"Unknown mode: {mode}. Must be one of: sql, rag, hybrid")
    return agents[mode]


# ---------------------------------------------------------------------------
# Shared utilities
# ---------------------------------------------------------------------------


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


def stream_agent_events(agent, question: str, thread_id: str, mode: str):
    """Generator that yields SSE-formatted events from agent execution.

    Event types:
        step   - intermediate reasoning (thinking, sql_query, sql_result, source)
        answer - final agent response
        done   - stream complete signal
    
    Args:
        agent: The agent to run
        question: User's question
        thread_id: Thread ID for conversation history
        mode: Agent mode ("sql", "rag", "hybrid") - history is limited only for "rag"
    """
    tracker = TokenTracker()
    config = {
        "configurable": {"thread_id": thread_id},
        "callbacks": [tracker],
    }

    # Get the number of messages already in the checkpoint so we skip them.
    # Without this, stream_mode="values" re-emits the full history on the
    # first step, causing previous answers to appear before the new one.
    existing_state = agent.get_state(config)
    
    # Limit conversation history to last 5 messages ONLY for RAG agent (token optimization)
    # SQL and hybrid agents need complete history for context
    if mode == "rag" and existing_state.values and "messages" in existing_state.values:
        messages = existing_state.values["messages"]
        if len(messages) > 5:
            # Keep only the last 5 messages
            trimmed_messages = messages[-5:]
            # Update the state with trimmed messages
            agent.update_state(config, {"messages": trimmed_messages})
            prev_count = len(trimmed_messages)
        else:
            prev_count = len(messages)
    else:
        prev_count = len(existing_state.values.get("messages", [])) if existing_state.values else 0

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
                tracker.track_from_metadata(msg)
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
                        elif tool_name == "retrieve_context":
                            yield _sse_event(
                                "step",
                                {
                                    "type": "thinking",
                                    "content": "Searching uploaded documents...",
                                },
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
                elif tool_name == "retrieve_context":
                    # Emit source event with retrieved context
                    yield _sse_event(
                        "step",
                        {"type": "source", "content": content},
                    )
                else:
                    yield _sse_event(
                        "step",
                        {"type": "thinking", "content": content},
                    )

    summary = tracker.summary()
    logger.info("[tokens] Request complete — %s", summary)
    yield _sse_event("done", {"status": "complete", **summary})


def _sse_event(event: str, data: dict) -> str:
    """Format a Server-Sent Event string."""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"
