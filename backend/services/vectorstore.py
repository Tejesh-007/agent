import chromadb
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

COLLECTION_NAME = "documents"


def create_embeddings(model_name: str = "models/gemini-embedding-001"):
    """Create Google Generative AI embeddings instance."""
    return GoogleGenerativeAIEmbeddings(model=model_name)


def create_vectorstore(
    host: str = "localhost",
    port: int = 8100,
    embedding_model: str = "models/gemini-embedding-001",
) -> Chroma:
    """Create a LangChain Chroma vectorstore connected to Docker ChromaDB.

    Args:
        host: ChromaDB server host.
        port: ChromaDB server port.
        embedding_model: Google embedding model name.

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
