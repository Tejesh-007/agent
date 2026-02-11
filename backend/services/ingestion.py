from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma


def _get_loader(file_path: str, file_type: str):
    """Return the appropriate LangChain document loader for the file type."""
    if file_type == "pdf":
        from langchain_community.document_loaders import PyPDFLoader
        return PyPDFLoader(file_path)
    elif file_type == "csv":
        from langchain_community.document_loaders import CSVLoader
        return CSVLoader(file_path)
    elif file_type == "txt":
        from langchain_community.document_loaders import TextLoader
        return TextLoader(file_path, encoding="utf-8")
    elif file_type == "docx":
        from langchain_community.document_loaders import Docx2txtLoader
        return Docx2txtLoader(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")


def ingest_document(
    file_path: str,
    document_id: str,
    filename: str,
    file_type: str,
    vectorstore: Chroma,
) -> int:
    """Load, split, embed, and store a document in ChromaDB.

    Args:
        file_path: Path to the saved file on disk.
        document_id: UUID for this document.
        filename: Original filename.
        file_type: File extension (pdf, csv, txt, docx).
        vectorstore: The Chroma vectorstore to add chunks to.

    Returns:
        Number of chunks created and stored.
    """
    # 1. Load document
    loader = _get_loader(file_path, file_type)
    docs = loader.load()

    # 2. Split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " "],
        add_start_index=True,
    )
    chunks = splitter.split_documents(docs)

    # 3. Add metadata to each chunk
    for i, chunk in enumerate(chunks):
        chunk.metadata.update({
            "document_id": document_id,
            "filename": filename,
            "chunk_index": i,
            "total_chunks": len(chunks),
        })
        # Preserve page number if present (from PDF loader)
        if "page" not in chunk.metadata:
            chunk.metadata["page"] = 0

    # 4. Add to vectorstore
    if chunks:
        vectorstore.add_documents(chunks)

    return len(chunks)
