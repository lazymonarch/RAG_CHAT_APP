import logging
from typing import Dict, Any, Optional
from datetime import datetime
from app.db.mongodb_models import User, UserAnalytics, Document, Conversation, Message
from app.schemas.user import UserProfileResponse

logger = logging.getLogger(__name__)


class ProfileService:
    """Service for managing user profiles and analytics."""
    
    async def get_user_profile(self, user_id: str) -> UserProfileResponse:
        """Get comprehensive user profile with statistics."""
        try:
            # Get user data
            user = await User.get(user_id)
            if not user:
                raise ValueError("User not found")
            
            # Get analytics
            analytics = await UserAnalytics.find_one(UserAnalytics.user_id == user_id)
            
            # Calculate statistics
            doc_count = await Document.find(Document.user_id == user_id).count()
            chat_count = await Conversation.find(Conversation.user_id == user_id).count()
            
            # Get total messages across all conversations
            conversations = await Conversation.find(Conversation.user_id == user_id).to_list()
            conversation_ids = [str(conv.id) for conv in conversations]
            
            # Count messages for each conversation
            message_count = 0
            for conv_id in conversation_ids:
                conv_message_count = await Message.find(Message.conversation_id == conv_id).count()
                message_count += conv_message_count
            
            logger.info(f"Profile stats for user {user_id}: docs={doc_count}, chats={chat_count}, messages={message_count}")
            
            # Calculate storage used
            documents = await Document.find(Document.user_id == user_id).to_list()
            storage_used = sum([doc.file_size for doc in documents])
            
            # Calculate storage percentage
            storage_percentage = (storage_used / user.storage_limit) * 100 if user.storage_limit > 0 else 0
            
            return UserProfileResponse(
                id=str(user.id),
                name=user.name or "Not Set",
                email=user.email,
                created_at=user.created_at,
                last_login=user.last_login,
                document_count=doc_count,
                chat_count=chat_count,
                message_count=message_count,
                storage_used=storage_used,
                storage_limit=user.storage_limit,
                storage_percentage=storage_percentage
            )
            
        except Exception as e:
            logger.error(f"Failed to get user profile: {e}")
            raise
    
    async def update_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> UserProfileResponse:
        """Update user profile information."""
        try:
            user = await User.get(user_id)
            if not user:
                raise ValueError("User not found")
            
            # Update allowed fields
            if "name" in profile_data:
                user.name = profile_data["name"]
            
            user.updated_at = datetime.utcnow()
            await user.save()
            
            # Return updated profile
            return await self.get_user_profile(user_id)
            
        except Exception as e:
            logger.error(f"Failed to update user profile: {e}")
            raise
    
    async def get_user_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get detailed user analytics."""
        try:
            analytics = await UserAnalytics.find_one(UserAnalytics.user_id == user_id)
            
            if not analytics:
                # Create default analytics if none exist
                analytics = UserAnalytics(
                    user_id=user_id,
                    total_documents=0,
                    total_conversations=0,
                    total_messages=0,
                    total_queries=0,
                    storage_used=0,
                    last_activity=datetime.utcnow()
                )
                await analytics.insert()
            
            return {
                "user_id": analytics.user_id,
                "total_documents": analytics.total_documents,
                "total_conversations": analytics.total_conversations,
                "total_messages": analytics.total_messages,
                "total_queries": analytics.total_queries,
                "storage_used": analytics.storage_used,
                "last_activity": analytics.last_activity,
                "created_at": analytics.created_at,
                "updated_at": analytics.updated_at
            }
            
        except Exception as e:
            logger.error(f"Failed to get user analytics: {e}")
            raise
    
    async def update_storage_usage(self, user_id: str):
        """Update storage usage for a user."""
        try:
            # Calculate current storage usage
            documents = await Document.find(Document.user_id == user_id).to_list()
            storage_used = sum([doc.file_size for doc in documents])
            
            # Update user storage_used
            user = await User.get(user_id)
            if user:
                user.storage_used = storage_used
                await user.save()
            
            # Update analytics
            analytics = await UserAnalytics.find_one(UserAnalytics.user_id == user_id)
            if analytics:
                analytics.storage_used = storage_used
                analytics.updated_at = datetime.utcnow()
                await analytics.save()
            
            logger.info(f"Updated storage usage for user {user_id}: {storage_used} bytes")
            
        except Exception as e:
            logger.error(f"Failed to update storage usage: {e}")
            raise


# Global profile service instance
profile_service = ProfileService()
