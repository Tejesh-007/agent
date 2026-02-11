from pathlib import Path

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

from core.agent import create_sql_agent, create_rag_agent, create_hybrid_agent
from services.db import get_database
from services.memory import create_memory
from services.vectorstore import create_vectorstore
from core.settings import Settings


def build_app(settings: Settings | None = None):
    """Initialize all application components.

    Returns:
        dict with keys: agents, db, vectorstore, settings
    """
    # Search for .env in current dir or parent
    env_path = Path(".env")
    if not env_path.exists():
        env_path = Path("../.env")
    load_dotenv(env_path)

    settings = settings or Settings()

    # Core components
    db = get_database(settings.db_url, settings.db_path)
    model = init_chat_model(settings.model_name)
    memory = create_memory()

    # ChromaDB vectorstore
    vectorstore = create_vectorstore(
        host=settings.chroma_host,
        port=settings.chroma_port,
        embedding_model=settings.embedding_model,
    )

    # Create all three agents sharing the same memory
    agents = {
        "sql": create_sql_agent(model, db, top_k=settings.top_k, checkpointer=memory),
        "rag": create_rag_agent(model, vectorstore, checkpointer=memory),
        "hybrid": create_hybrid_agent(model, db, vectorstore, top_k=settings.top_k, checkpointer=memory),
    }

    # Ensure uploads directory exists
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)

    return {
        "agents": agents,
        "db": db,
        "vectorstore": vectorstore,
        "settings": settings,
    }
