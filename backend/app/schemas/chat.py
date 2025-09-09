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
    is_active: bool
    message_count: Optional[int] = None


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
    message_count: int
