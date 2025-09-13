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
    last_login: Optional[datetime] = None
    storage_used: int = 0  # in bytes
    storage_limit: int = 100 * 1024 * 1024  # 100MB default limit
    is_active: bool = True
    
    class Settings:
        name = "users"


class Conversation(Document):
    """Conversation model to store chat sessions."""
    user_id: str  # Reference to User._id
    title: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_message_at: Optional[datetime] = None
    message_count: int = 0
    is_active: bool = True
    
    class Settings:
        name = "conversations"


class Message(Document):
    """Message model to store individual chat messages."""
    conversation_id: str  # Reference to Conversation._id
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    sources: Optional[List[dict]] = None  # Which documents/chunks were used
    response_time: Optional[float] = None  # in seconds
    token_count: Optional[int] = None
    metadata: Optional[dict] = None  # For storing additional info
    
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
    query_count: int = 0  # How many times used in queries
    last_accessed: Optional[datetime] = None
    
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


class UserAnalytics(Document):
    """User analytics model for tracking usage statistics."""
    user_id: str  # Reference to User._id
    total_documents: int = 0
    total_conversations: int = 0
    total_messages: int = 0
    total_queries: int = 0
    storage_used: int = 0  # in bytes
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "user_analytics"
