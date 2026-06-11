"""Document Q&A — PDF upload, Pinecone upsert, RAG query with citations."""
from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import get_db
from models.schemas import (
    DocumentListItem,
    DocumentQueryRequest,
    DocumentQueryResponse,
    DocumentUploadResponse,
)
from services.rag_service import delete_namespace, query_document, upsert_chunks
from utils.chunking import chunk_pages, extract_text_from_pdf

router = APIRouter(prefix="/documents", tags=["document-qa"])


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: Annotated[UploadFile, File(...)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DocumentUploadResponse:
    """Upload a PDF, extract text, embed, and upsert into Pinecone."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    doc_id = str(uuid.uuid4())
    namespace = f"doc-{doc_id}"

    content = await file.read()
    pages = extract_text_from_pdf(content)
    if not pages:
        raise HTTPException(status_code=422, detail="Could not extract text from PDF")

    chunks = chunk_pages(pages)
    if not chunks:
        raise HTTPException(status_code=422, detail="Document produced no indexable chunks")

    chunk_count = upsert_chunks(chunks, namespace)

    await db.execute(
        text(
            "INSERT INTO documents (id, filename, namespace, chunk_count, created_at) "
            "VALUES (:id, :filename, :namespace, :chunk_count, NOW())"
        ),
        {
            "id": doc_id,
            "filename": file.filename,
            "namespace": namespace,
            "chunk_count": chunk_count,
        },
    )
    await db.commit()

    return DocumentUploadResponse(
        document_id=doc_id,
        filename=file.filename,
        chunk_count=chunk_count,
        namespace=namespace,
    )


@router.post("/query", response_model=DocumentQueryResponse)
async def query_doc(request: DocumentQueryRequest) -> DocumentQueryResponse:
    """Answer a question against an uploaded document using RAG."""
    namespace = f"doc-{request.document_id}"
    answer, citations = await query_document(request.question, namespace)
    # DocumentQueryResponse only has `answer` and `citations` fields
    return DocumentQueryResponse(
        answer=answer,
        citations=citations,
    )


@router.get("/", response_model=list[DocumentListItem])
async def list_documents(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> list[DocumentListItem]:
    """List all uploaded documents."""
    result = await db.execute(
        text(
            "SELECT id, filename, created_at "
            "FROM documents ORDER BY created_at DESC LIMIT 100"
        )
    )
    return [
        DocumentListItem(
            id=row.id,
            filename=row.filename,
            uploaded_at=row.created_at,
        )
        for row in result.fetchall()
    ]


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """Delete a document and its Pinecone vectors."""
    result = await db.execute(
        text("SELECT id FROM documents WHERE id = :id"),
        {"id": document_id},
    )
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Document not found")

    delete_namespace(f"doc-{document_id}")
    await db.execute(
        text("DELETE FROM documents WHERE id = :id"),
        {"id": document_id},
    )
    await db.commit()
    return {"deleted": document_id}
