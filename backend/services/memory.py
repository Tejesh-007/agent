from langgraph.checkpoint.memory import MemorySaver


def create_memory():
    """Create an in-memory checkpointer for thread conversation history.

    For production, replace with SqliteSaver or PostgresSaver
    for persistence across restarts.
    """
    return MemorySaver()
