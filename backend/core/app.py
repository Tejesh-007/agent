from pathlib import Path

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

from core.agent import create_sql_agent
from services.db import get_database
from services.memory import create_memory
from core.settings import Settings


def build_app(settings: Settings | None = None):
    """Initialize all application components.

    Returns:
        tuple: (agent, db, settings)
    """
    # Search for .env in current dir or parent
    env_path = Path(".env")
    if not env_path.exists():
        env_path = Path("../.env")
    load_dotenv(env_path)

    settings = settings or Settings()
    db = get_database(settings.db_url, settings.db_path)
    model = init_chat_model(settings.model_name)
    memory = create_memory()
    agent = create_sql_agent(model, db, top_k=settings.top_k, checkpointer=memory)

    return agent, db, settings
