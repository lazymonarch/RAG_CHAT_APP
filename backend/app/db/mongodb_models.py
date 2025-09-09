from beanie import Document, Indexed
from pydantic import Field, EmailStr
from typing import List, Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"


class User(Document):
    """User model for authentication and user management."""
    email: Indexed(EmailStr, unique=True)
    hashed_password: str
    name: Optional[str] = None  # User's display name
    role: UserRole = UserRole.USER
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "users"


class Conversation(Document):
    """Conversation model to store chat sessions."""
    user_id: str  # Reference to User._id
    title: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    
    class Settings:
        name = "conversations"


class Message(Document):
    """Message model to store individual chat messages."""
    conversation_id: str  # Reference to Conversation._id
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[dict] = None  # For storing additional info like sources
    
    class Settings:
        name = "messages"


class Document(Document):
    """Document model to store uploaded file metadata."""
    user_id: str  # Reference to User._id
    filename: str
    original_filename: str
    file_type: str  # pdf, txt, docx, doc
    file_size: int  # in bytes
    chunk_count: int
    pinecone_ids: List[str]  # List of Pinecone vector IDs
    upload_timestamp: datetime = Field(default_factory=datetime.utcnow)
    processing_status: str = "completed"  # pending, processing, completed, failed
    error_message: Optional[str] = None
    
    class Settings:
        name = "documents"


class DocumentChunk(Document):
    """Document chunk model for detailed chunk information."""
    document_id: str  # Reference to Document._id
    user_id: str  # Reference to User._id
    chunk_index: int
    content: str
    pinecone_id: str  # Pinecone vector ID
    token_count: int
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    chunk_count: int
    pinecone_ids: List[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "document_chunks"
