import logging

import chromadb
from langchain_chroma import Chroma

logger = logging.getLogger(__name__)

COLLECTION_NAME = "documents-qwen"


def create_embeddings(model_name: str):
    """Create an embeddings instance based on the model name.

    Provider is auto-detected from the model name prefix:

      - ``openai:`` or ``text-embedding-`` → OpenAI  (langchain-openai)
      - ``Qwen/`` or ``huggingface:``      → HuggingFace local (sentence-transformers)
      - anything else                       → Google Generative AI (langchain-google-genai)

    Examples::

        create_embeddings("openai:text-embedding-3-small")
        create_embeddings("text-embedding-3-small")
        create_embeddings("Qwen/Qwen3-Embedding-0.6B")
        create_embeddings("huggingface:sentence-transformers/all-MiniLM-L6-v2")
        create_embeddings("models/gemini-embedding-001")

    Note: switching to a model with a different embedding dimension (e.g.
    from Google 768-d to Qwen 1024-d) requires recreating the ChromaDB
    collection and re-ingesting all documents.
    """
    # --- OpenAI ---
    if model_name.startswith("text-embedding-") or model_name.startswith("openai:"):
        from langchain_openai import OpenAIEmbeddings

        clean_name = model_name.removeprefix("openai:")
        logger.info("Using OpenAI embeddings: %s", clean_name)
        return OpenAIEmbeddings(model=clean_name)

    # --- HuggingFace / Qwen (local) ---
    if model_name.startswith("Qwen/") or model_name.startswith("huggingface:"):
        from langchain_huggingface import HuggingFaceEmbeddings

        clean_name = model_name.removeprefix("huggingface:")
        logger.info("Using HuggingFace embeddings: %s", clean_name)
        return HuggingFaceEmbeddings(
            model_name=clean_name,
            encode_kwargs={"normalize_embeddings": True},
        )

    # --- Google Generative AI (default) ---
    from langchain_google_genai import GoogleGenerativeAIEmbeddings

    logger.info("Using Google Generative AI embeddings: %s", model_name)
    return GoogleGenerativeAIEmbeddings(model=model_name)


def create_vectorstore(
    host: str,
    port: int,
    embedding_model: str,
) -> Chroma:
    """Create a LangChain Chroma vectorstore connected to Docker ChromaDB.

    Args:
        host: ChromaDB server host.
        port: ChromaDB server port.
        embedding_model: Embedding model name (auto-detects provider).

    Returns:
        LangChain Chroma wrapper ready for similarity search and document add.
    """
    client = chromadb.HttpClient(host=host, port=port)
    embeddings = create_embeddings(embedding_model)

    return Chroma(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
    )


def delete_document_chunks(vectorstore: Chroma, document_id: str) -> int:
    """Delete all vector chunks belonging to a specific document.

    Args:
        vectorstore: The Chroma vectorstore instance.
        document_id: UUID of the document whose chunks to delete.

    Returns:
        Number of chunks deleted.
    """
    collection = vectorstore._collection
    results = collection.get(where={"document_id": document_id})
    ids = results.get("ids", [])
    if ids:
        collection.delete(ids=ids)
    return len(ids)
