from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class MessageBase(BaseModel):
    content: str
    role: str  # "user" or "assistant"


class MessageCreate(MessageBase):
    conversation_id: str


class MessageResponse(MessageBase):
    id: str
    conversation_id: str
    timestamp: datetime
    sources: Optional[List[dict]] = None
    response_time: Optional[float] = None
    token_count: Optional[int] = None
    metadata: Optional[dict] = None


class ConversationBase(BaseModel):
    title: str


class ConversationCreate(ConversationBase):
    pass


class ConversationResponse(ConversationBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    last_message_at: Optional[datetime] = None
    message_count: int = 0
    is_active: bool = True


class ChatQuery(BaseModel):
    query: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    message: str
    conversation_id: str
    sources: Optional[List[dict]] = None
    timestamp: datetime


class ConversationListResponse(BaseModel):
    conversations: List[ConversationResponse]
    total: int


# New schemas for OpenAI implementation
class MessageIn(BaseModel):
    content: str


class MessageOut(BaseModel):
    id: str
    role: str
    content: str
    timestamp: datetime
    usage: Optional[Dict[str, Any]] = None


class ConversationHistory(BaseModel):
    id: str
    title: str
    created_at: datetime
    last_message_at: Optional[datetime] = None
    message_count: int


class ConversationStartResponse(BaseModel):
    """Response when starting a new conversation."""
    conversation_id: str
    title: str
    created_at: datetime


class ChatQueryResponse(BaseModel):
    """Enhanced response for chat queries."""
    message: str
    conversation_id: str
    sources: Optional[List[dict]] = None
    response_time: float
    token_count: Optional[int] = None
    timestamp: datetime


class ConversationDetailResponse(BaseModel):
    """Detailed conversation with messages."""
    id: str
    title: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    last_message_at: Optional[datetime] = None
    message_count: int
    is_active: bool
    messages: List[MessageResponse]
