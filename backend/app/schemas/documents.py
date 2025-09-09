from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class DocumentBase(BaseModel):
    filename: str
    file_type: str


class DocumentCreate(DocumentBase):
    original_filename: str
    file_size: int


class DocumentResponse(DocumentBase):
    id: str
    user_id: str
    original_filename: str
    file_size: int
    chunk_count: int
    upload_timestamp: datetime
    processing_status: str
    error_message: Optional[str] = None


class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int


class DocumentChunkResponse(BaseModel):
    id: str
    document_id: str
    chunk_index: int
    content: str
    token_count: int
    created_at: datetime


class UploadResponse(BaseModel):
    message: str
    document_id: str
    filename: str
    chunk_count: int
    processing_status: str


class DocumentUploadRequest(BaseModel):
    filename: str
    file_type: str
    file_size: int
