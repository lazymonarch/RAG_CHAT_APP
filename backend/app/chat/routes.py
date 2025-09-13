from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
import logging
from app.schemas.chat import (
    MessageIn, MessageOut, ConversationHistory, 
    ConversationStartResponse, ChatQueryResponse, 
    ConversationDetailResponse
)
from app.chat.service import openai_chat_service
from app.chat.conversation_service import conversation_service
from app.vector.vector_service import vector_service
from app.dependencies import get_current_user
from app.db.mongodb_models import User, Conversation, Message
from app.core.config import settings

router = APIRouter(prefix="/chat", tags=["chat"])
logger = logging.getLogger(__name__)


@router.post("/query", response_model=MessageOut)
async def chat_query(
    message: MessageIn,
    current_user: User = Depends(get_current_user)
):
    """Process a chat query with RAG."""
    try:
        # Initialize services if needed
        await vector_service.initialize()
        await openai_chat_service.initialize()
        
        # Search for relevant content
        search_results = await vector_service.search_similar_content(
            query=message.content,
            user_id=str(current_user.id),
            top_k=settings.TOP_K_RESULTS
        )
        
        # Build context from search results
        context = "\n\n".join([result['text'] for result in search_results])
        
        # Generate response using OpenAI
        response_data = await openai_chat_service.generate_response(
            query=message.content,
            context=context
        )
        
        # Save conversation to database
        conversation = Conversation(
            user_id=str(current_user.id),
            title=message.content[:50] + "..." if len(message.content) > 50 else message.content
        )
        await conversation.insert()
        
        # Save user message
        user_message = Message(
            conversation_id=str(conversation.id),
            role="user",
            content=message.content
        )
        await user_message.insert()
        
        # Save assistant response
        assistant_message = Message(
            conversation_id=str(conversation.id),
            role="assistant",
            content=response_data["response"]
        )
        await assistant_message.insert()
        
        return MessageOut(
            id=str(assistant_message.id),
            role="assistant",
            content=response_data["response"],
            timestamp=assistant_message.timestamp,
            usage=response_data["usage"]
        )
        
    except Exception as e:
        logger.error(f"Chat query failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chat query"
        )


@router.get("/history", response_model=List[ConversationHistory])
async def get_chat_history(
    current_user: User = Depends(get_current_user)
):
    """Get chat history for the current user."""
    try:
        conversations = await Conversation.find(
            Conversation.user_id == str(current_user.id)
        ).to_list()
        
        history = []
        for conv in conversations:
            # Get messages for this conversation
            messages = await Message.find(
                Message.conversation_id == str(conv.id)
            ).to_list()
            
            history.append(ConversationHistory(
                id=str(conv.id),
                title=conv.title,
                created_at=conv.created_at,
                message_count=len(messages)
            ))
        
        return history
        
    except Exception as e:
        logger.error(f"Failed to get chat history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve chat history"
        )


@router.get("/conversation/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get messages for a specific conversation."""
    try:
        # Verify conversation belongs to user
        conversation = await Conversation.get(conversation_id)
        if not conversation or conversation.user_id != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Get messages
        messages = await Message.find(
            Message.conversation_id == conversation_id
        ).to_list()
        
        return {
            "conversation_id": conversation_id,
            "title": conversation.title,
            "created_at": conversation.created_at,
            "messages": [
                {
                    "id": str(msg.id),
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp
                }
                for msg in messages
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversation"
        )


@router.post("/start", response_model=ConversationStartResponse)
async def start_conversation(
    current_user: User = Depends(get_current_user)
):
    """Start a new conversation."""
    try:
        result = await conversation_service.start_conversation(str(current_user.id))
        return result
        
    except Exception as e:
        logger.error(f"Failed to start conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start conversation"
        )


@router.post("/{conversation_id}/query", response_model=ChatQueryResponse)
async def send_message(
    conversation_id: str,
    message: MessageIn,
    current_user: User = Depends(get_current_user)
):
    """Send a message to a conversation."""
    try:
        result = await conversation_service.send_message(
            conversation_id=conversation_id,
            user_message=message.content,
            user_id=str(current_user.id)
        )
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send message"
        )


@router.get("/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation_detail(
    conversation_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a conversation with all its messages."""
    try:
        result = await conversation_service.get_conversation(
            conversation_id=conversation_id,
            user_id=str(current_user.id)
        )
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to get conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get conversation"
        )


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a conversation and all its messages."""
    try:
        result = await conversation_service.delete_conversation(
            conversation_id=conversation_id,
            user_id=str(current_user.id)
        )
        return {"success": result}
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to delete conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete conversation"
        )


@router.post("/test")
async def test_chat(
    message: MessageIn,
    current_user: User = Depends(get_current_user)
):
    """Test OpenAI chat without RAG (simple response)."""
    try:
        await openai_chat_service.initialize()
        
        response_data = await openai_chat_service.generate_simple_response(
            query=message.content
        )
        
        return {
            "response": response_data["response"],
            "usage": response_data["usage"]
        }
        
    except Exception as e:
        logger.error(f"Test chat failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process test query"
        )
