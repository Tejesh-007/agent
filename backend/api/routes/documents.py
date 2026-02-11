import os
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File

from models.schemas import DocumentResponse
from services.ingestion import ingest_document
from services.vectorstore import delete_document_chunks
from api.dependencies import get_document_store, get_vectorstore, get_settings

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=list[DocumentResponse])
async def list_documents(store=Depends(get_document_store)):
    """List all uploaded documents."""
    return store.list_all()


@router.post("", response_model=DocumentResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    store=Depends(get_document_store),
    vectorstore=Depends(get_vectorstore),
    settings=Depends(get_settings),
):
    """Upload and process a document.

    1. Validates file type and size.
    2. Saves raw file to uploads/ directory.
    3. Runs ingestion pipeline (load, split, embed, store in ChromaDB).
    4. Returns document metadata with processing status.
    """
    # Validate file type
    filename = file.filename or "unknown"
    file_ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if file_ext not in settings.allowed_file_types:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{file_ext}' not allowed. Allowed: {settings.allowed_file_types}",
        )

    # Read file content
    content = await file.read()
    file_size = len(content)

    # Validate file size
    max_bytes = settings.max_file_size_mb * 1024 * 1024
    if file_size > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File too large ({file_size} bytes). Max: {max_bytes} bytes.",
        )

    # Save file to uploads directory
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Create document record first to get the ID
    doc = store.create(
        filename=filename,
        file_type=file_ext,
        file_size=file_size,
        file_path="",  # Will be updated after save
    )

    # Save with document_id prefix to avoid collisions
    safe_filename = f"{doc['id']}_{filename}"
    file_path = upload_dir / safe_filename
    file_path.write_bytes(content)

    # Update file path
    store.update(doc["id"], file_path=str(file_path))

    # Run ingestion pipeline
    try:
        chunk_count = ingest_document(
            file_path=str(file_path),
            document_id=doc["id"],
            filename=filename,
            file_type=file_ext,
            vectorstore=vectorstore,
        )
        store.update(doc["id"], status="ready", chunk_count=chunk_count)
    except Exception as e:
        store.update(doc["id"], status="error", error_message=str(e))

    return store.get(doc["id"])


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str, store=Depends(get_document_store)):
    """Get document metadata by ID."""
    doc = store.get(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: str,
    store=Depends(get_document_store),
    vectorstore=Depends(get_vectorstore),
):
    """Delete a document and all its vector chunks from ChromaDB."""
    doc = store.get(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete vector chunks from ChromaDB
    try:
        delete_document_chunks(vectorstore, document_id)
    except Exception:
        pass  # Continue even if ChromaDB deletion fails

    # Delete the raw file from disk
    file_path = doc.get("file_path", "")
    if file_path and os.path.exists(file_path):
        os.remove(file_path)

    # Delete metadata
    store.delete(document_id)
