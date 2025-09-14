import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.db.mongodb_models import Conversation, Message, User, UserAnalytics
from app.schemas.chat import ConversationStartResponse, ChatQueryResponse, ConversationDetailResponse, MessageResponse
from app.vector.vector_service import vector_service
from app.chat.service import openai_chat_service
from app.core.config import settings

logger = logging.getLogger(__name__)


class ConversationService:
    """Service for managing conversations and messages."""
    
    def __init__(self):
        self.vector_service = vector_service
        self.chat_service = openai_chat_service
    
    async def start_conversation(self, user_id: str, title: Optional[str] = None) -> ConversationStartResponse:
        """Start a new conversation and return conversation details."""
        try:
            # Generate title if not provided
            if not title:
                title = f"Chat {datetime.now().strftime('%B %d, %Y')}"
            
            # Create conversation
            conversation = Conversation(
                user_id=user_id,
                title=title,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                last_message_at=datetime.utcnow(),
                message_count=0,
                is_active=True
            )
            await conversation.insert()
            
            # Update user analytics
            await self._update_user_analytics(user_id, "conversation_created")
            
            logger.info(f"Created new conversation {conversation.id} for user {user_id}")
            
            return ConversationStartResponse(
                conversation_id=str(conversation.id),
                title=conversation.title,
                created_at=conversation.created_at
            )
            
        except Exception as e:
            logger.error(f"Failed to start conversation: {e}")
            raise
    
    async def start_document_conversation(
        self, 
        user_id: str, 
        document_ids: List[str], 
        title: Optional[str] = None
    ) -> 'DocumentChatStartResponse':
        """Start a new document-scoped conversation."""
        try:
            from app.db.mongodb_models import Document
            from app.vector.vector_service import vector_service
            
            # Get document names from Pinecone metadata since we're using Pinecone IDs
            document_names = []
            try:
                # Search for vectors to get document names
                search_results = await vector_service.search_similar_content(
                    query="",  # Empty query to get all vectors
                    user_id=user_id,
                    top_k=1000  # Large number to get all vectors
                )
                
                # Map Pinecone document IDs to filenames
                doc_id_to_filename = {}
                for result in search_results:
                    doc_id = result['metadata'].get('document_id')
                    filename = result['metadata'].get('filename')
                    if doc_id and filename:
                        doc_id_to_filename[doc_id] = filename
                
                # Get document names for the requested document IDs
                for doc_id in document_ids:
                    filename = doc_id_to_filename.get(doc_id, f"Document {doc_id[:8]}")
                    document_names.append(filename)
                    
            except Exception as e:
                logger.warning(f"Failed to get document names from Pinecone: {e}")
                # Fallback to generic names
                document_names = [f"Document {doc_id[:8]}" for doc_id in document_ids]
            
            # Generate title if not provided
            if not title:
                if len(document_names) == 1:
                    title = f"Chat: {document_names[0]}"
                else:
                    title = f"Chat: {', '.join(document_names[:2])}{'...' if len(document_names) > 2 else ''}"
            
            # Create conversation
            conversation = Conversation(
                user_id=user_id,
                title=title,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                last_message_at=datetime.utcnow(),
                message_count=0,
                is_active=True,
                chat_type="document",
                selected_document_ids=document_ids,
                document_names=document_names
            )
            await conversation.insert()
            
            # Update user analytics
            await self._update_user_analytics(user_id, "conversation_created")
            
            logger.info(f"Created new document conversation {conversation.id} for user {user_id} with {len(document_ids)} documents")
            
            from app.schemas.chat import DocumentChatStartResponse
            
            return DocumentChatStartResponse(
                conversation_id=str(conversation.id),
                title=conversation.title,
                created_at=conversation.created_at,
                selected_document_ids=conversation.selected_document_ids,
                document_names=conversation.document_names
            )
            
        except Exception as e:
            logger.error(f"Failed to start document conversation: {e}")
            raise
    
    async def send_message(
        self, 
        conversation_id: str, 
        user_message: str, 
        user_id: str
    ) -> ChatQueryResponse:
        """Send a message to a conversation and return the response."""
        try:
            start_time = datetime.utcnow()
            
            # Get conversation
            conversation = await Conversation.get(conversation_id)
            if not conversation or conversation.user_id != user_id:
                raise ValueError("Conversation not found or access denied")
            
            # Save user message
            user_msg = Message(
                conversation_id=conversation_id,
                role="user",
                content=user_message,
                timestamp=datetime.utcnow()
            )
            await user_msg.insert()
            
            # Get conversation history for context
            conversation_history = await self._get_conversation_history(conversation_id)
            
            # Process with RAG (document-scoped if applicable)
            if conversation.chat_type == "document" and conversation.selected_document_ids:
                rag_response = await self._process_document_rag_query(
                    user_message, user_id, conversation_history, conversation.selected_document_ids
                )
            else:
                rag_response = await self._process_rag_query(user_message, user_id, conversation_history)
            
            # Calculate response time
            response_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Save assistant response
            assistant_msg = Message(
                conversation_id=conversation_id,
                role="assistant",
                content=rag_response["response"],
                timestamp=datetime.utcnow(),
                sources=rag_response.get("sources", []),
                response_time=response_time,
                token_count=rag_response.get("usage", {}).get("total_tokens", 0)
            )
            await assistant_msg.insert()
            
            # Update conversation
            conversation.message_count += 1
            conversation.last_message_at = datetime.utcnow()
            conversation.updated_at = datetime.utcnow()
            await conversation.save()
            
            # Update user analytics
            await self._update_user_analytics(user_id, "message_sent")
            
            logger.info(f"Processed message in conversation {conversation_id}")
            
            return ChatQueryResponse(
                message=rag_response["response"],
                conversation_id=conversation_id,
                sources=rag_response.get("sources", []),
                response_time=response_time,
                token_count=rag_response.get("usage", {}).get("total_tokens", 0),
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            raise
    
    async def get_conversation(self, conversation_id: str, user_id: str) -> ConversationDetailResponse:
        """Get a conversation with all its messages."""
        try:
            # Get conversation
            conversation = await Conversation.get(conversation_id)
            if not conversation:
                logger.warning(f"Conversation {conversation_id} not found")
                raise ValueError("Conversation not found")
            
            # Debug logging
            logger.info(f"Conversation {conversation_id} found. User ID in conversation: {conversation.user_id}, Requested user ID: {user_id}")
            
            if conversation.user_id != user_id:
                logger.warning(f"Access denied: conversation user_id ({conversation.user_id}) != requested user_id ({user_id})")
                raise ValueError("Conversation not found or access denied")
            
            # Get messages
            messages = await Message.find(Message.conversation_id == conversation_id).sort("timestamp").to_list()
            
            # Convert to response format
            message_responses = []
            for msg in messages:
                message_responses.append(MessageResponse(
                    id=str(msg.id),
                    conversation_id=str(msg.conversation_id),
                    role=msg.role,
                    content=msg.content,
                    timestamp=msg.timestamp,
                    sources=msg.sources,
                    response_time=msg.response_time,
                    token_count=msg.token_count,
                    metadata=msg.metadata
                ))
            
            return ConversationDetailResponse(
                id=str(conversation.id),
                title=conversation.title,
                user_id=conversation.user_id,
                created_at=conversation.created_at,
                updated_at=conversation.updated_at,
                last_message_at=conversation.last_message_at,
                message_count=conversation.message_count,
                is_active=conversation.is_active,
                messages=message_responses
            )
            
        except Exception as e:
            logger.error(f"Failed to get conversation: {e}")
            raise
    
    async def get_user_conversations(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all conversations for a user."""
        try:
            conversations = await Conversation.find(
                Conversation.user_id == user_id,
                Conversation.is_active == True
            ).sort("-last_message_at").to_list()
            
            conversation_list = []
            for conv in conversations:
                conversation_list.append({
                    "id": str(conv.id),
                    "title": conv.title,
                    "created_at": conv.created_at,
                    "last_message_at": conv.last_message_at,
                    "message_count": conv.message_count,
                    "chat_type": getattr(conv, 'chat_type', 'universal'),
                    "selected_document_ids": getattr(conv, 'selected_document_ids', []),
                    "document_names": getattr(conv, 'document_names', [])
                })
            
            return conversation_list
            
        except Exception as e:
            logger.error(f"Failed to get user conversations: {e}")
            raise
    
    async def delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        """Delete a conversation and all its messages."""
        try:
            # Get conversation
            conversation = await Conversation.get(conversation_id)
            if not conversation or conversation.user_id != user_id:
                raise ValueError("Conversation not found or access denied")
            
            # Delete all messages
            await Message.find(Message.conversation_id == conversation_id).delete()
            
            # Delete conversation
            await conversation.delete()
            
            # Update user analytics
            await self._update_user_analytics(user_id, "conversation_deleted")
            
            logger.info(f"Deleted conversation {conversation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete conversation: {e}")
            raise
    
    async def _get_conversation_history(self, conversation_id: str, limit: int = 10) -> List[Dict[str, str]]:
        """Get recent conversation history for context."""
        try:
            messages = await Message.find(
                Message.conversation_id == conversation_id
            ).sort("-timestamp").limit(limit).to_list()
            
            # Reverse to get chronological order
            messages.reverse()
            
            history = []
            for msg in messages:
                history.append({
                    "role": msg.role,
                    "content": msg.content
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Failed to get conversation history: {e}")
            return []
    
    async def _process_rag_query(
        self, 
        query: str, 
        user_id: str, 
        conversation_history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Process a query using RAG pipeline."""
        try:
            # Search for relevant documents
            search_results = await self.vector_service.search_similar_content(
                query=query,
                user_id=user_id,
                top_k=settings.TOP_K_RESULTS
            )
            
            # Extract context from search results
            context = ""
            sources = []
            
            for result in search_results:
                context += f"\n{result['text']}\n"
                sources.append({
                    "document_id": result.get("document_id"),
                    "filename": result.get("filename"),
                    "chunk_index": result.get("chunk_index"),
                    "score": result.get("score")
                })
            
            # Generate response using OpenAI
            response = await self.chat_service.generate_response(
                query=query,
                context=context,
                conversation_history=conversation_history
            )
            
            return {
                "response": response["response"],
                "sources": sources,
                "usage": response["usage"]
            }
            
        except Exception as e:
            logger.error(f"Failed to process RAG query: {e}")
            raise
    
    async def _process_document_rag_query(
        self, 
        query: str, 
        user_id: str, 
        conversation_history: List[Dict[str, str]],
        document_ids: List[str]
    ) -> Dict[str, Any]:
        """Process a query using document-scoped RAG pipeline."""
        try:
            # Search for relevant content within specific documents
            search_results = await self.vector_service.search_document_scoped_content(
                query=query,
                user_id=user_id,
                document_ids=document_ids,
                top_k=settings.TOP_K_RESULTS
            )
            
            # Extract context from search results
            context = ""
            sources = []
            
            for result in search_results:
                context += f"\n{result['text']}\n"
                sources.append({
                    "document_id": result.get("metadata", {}).get("document_id"),
                    "filename": result.get("metadata", {}).get("filename"),
                    "chunk_index": result.get("metadata", {}).get("chunk_index"),
                    "score": result.get("score")
                })
            
            # Generate response using OpenAI
            response = await self.chat_service.generate_response(
                query=query,
                context=context,
                conversation_history=conversation_history
            )
            
            return {
                "response": response["response"],
                "sources": sources,
                "usage": response["usage"]
            }
            
        except Exception as e:
            logger.error(f"Failed to process document RAG query: {e}")
            raise
    
    async def _update_user_analytics(self, user_id: str, action: str):
        """Update user analytics based on action."""
        try:
            analytics = await UserAnalytics.find_one(UserAnalytics.user_id == user_id)
            
            if not analytics:
                analytics = UserAnalytics(
                    user_id=user_id,
                    total_documents=0,
                    total_conversations=0,
                    total_messages=0,
                    total_queries=0,
                    storage_used=0,
                    last_activity=datetime.utcnow()
                )
            
            # Update based on action
            if action == "conversation_created":
                analytics.total_conversations += 1
            elif action == "message_sent":
                analytics.total_messages += 1
            elif action == "conversation_deleted":
                analytics.total_conversations = max(0, analytics.total_conversations - 1)
            
            analytics.last_activity = datetime.utcnow()
            analytics.updated_at = datetime.utcnow()
            
            await analytics.save()
            
        except Exception as e:
            logger.error(f"Failed to update user analytics: {e}")


# Global conversation service instance
conversation_service = ConversationService()
