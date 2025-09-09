from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import List
import logging
from app.schemas.documents import DocumentResponse, DocumentListResponse, UploadResponse
from app.documents.service import document_service
from app.dependencies import get_current_user
from app.db.mongodb_models import User

router = APIRouter(prefix="/documents", tags=["documents"])
logger = logging.getLogger(__name__)


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload and process a document."""
    try:
        # Read file content
        file_content = await file.read()
        
        # Process document
        result = await document_service.process_document(
            file_content=file_content,
            filename=file.filename,
            user_id=str(current_user.id)
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return UploadResponse(
            message="Document uploaded and processed successfully",
            document_id=result["document_id"],
            filename=result["filename"],
            chunk_count=result["chunk_count"],
            processing_status=result["processing_status"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document upload failed"
        )


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    current_user: User = Depends(get_current_user)
):
    """Get all documents for the current user."""
    try:
        documents = await document_service.get_user_documents(str(current_user.id))
        
        return DocumentListResponse(
            documents=documents,
            total=len(documents)
        )
        
    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve documents"
        )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a specific document by ID."""
    try:
        from app.db.mongodb_models import Document as DocumentModel
        
        document = await DocumentModel.get(document_id)
        
        if not document or document.user_id != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        return DocumentResponse(
            id=str(document.id),
            user_id=document.user_id,
            filename=document.filename,
            original_filename=document.original_filename,
            file_type=document.file_type,
            file_size=document.file_size,
            chunk_count=document.chunk_count,
            upload_timestamp=document.upload_timestamp,
            processing_status=document.processing_status,
            error_message=document.error_message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve document"
        )


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a document and its vectors."""
    try:
        result = await document_service.delete_document(
            document_id=document_id,
            user_id=str(current_user.id)
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return {"message": result["message"]}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete document"
        )


@router.get("/{document_id}/chunks")
async def get_document_chunks(
    document_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get chunks for a specific document."""
    try:
        from app.db.mongodb_models import Document as DocumentModel, DocumentChunk
        
        # Verify document ownership
        document = await DocumentModel.get(document_id)
        if not document or document.user_id != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Get chunks
        chunks = await DocumentChunk.find(
            DocumentChunk.document_id == document_id
        ).to_list()
        
        return {
            "document_id": document_id,
            "chunks": [
                {
                    "id": str(chunk.id),
                    "chunk_index": chunk.chunk_index,
                    "content": chunk.content,
                    "token_count": chunk.token_count,
                    "created_at": chunk.created_at
                }
                for chunk in chunks
            ],
            "total_chunks": len(chunks)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get document chunks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve document chunks"
        )
