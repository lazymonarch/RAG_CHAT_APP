"""
Service for comprehensive user profile deletion.
Removes all user data from MongoDB and Pinecone.
"""
import logging
from typing import Dict, Any
from app.db.mongodb_models import User, Conversation, Message, Document, DocumentChunk
from app.vector.pinecone_client import pinecone_client
from app.vector.vector_service import vector_service

logger = logging.getLogger(__name__)


class UserDeleteService:
    """Service for comprehensive user data deletion."""
    
    def __init__(self):
        self.pinecone = pinecone_client
        self.vector_service = vector_service
    
    async def delete_user_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Delete user profile and all associated data.
        
        This function removes:
        1. User record from MongoDB
        2. All conversations and messages
        3. All documents and chunk details
        4. All vectors from Pinecone
        5. All associated metadata
        
        Args:
            user_id: The user ID to delete
            
        Returns:
            Dict with deletion results and statistics
        """
        try:
            logger.info(f"Starting comprehensive deletion for user: {user_id}")
            
            # Get user record first
            user = await User.get(user_id)
            if not user:
                return {
                    "success": False,
                    "error": "User not found",
                    "deleted_items": {}
                }
            
            deletion_stats = {
                "user_id": user_id,
                "user_email": user.email,
                "deleted_items": {
                    "conversations": 0,
                    "messages": 0,
                    "documents": 0,
                    "chunk_details": 0,
                    "pinecone_vectors": 0
                }
            }
            
            # 1. Delete all conversations and messages
            conversations = await Conversation.find(Conversation.user_id == user_id).to_list()
            for conversation in conversations:
                # Delete all messages in this conversation
                messages = await Message.find(Message.conversation_id == str(conversation.id)).to_list()
                for message in messages:
                    await message.delete()
                    deletion_stats["deleted_items"]["messages"] += 1
                
                # Delete the conversation
                await conversation.delete()
                deletion_stats["deleted_items"]["conversations"] += 1
            
            logger.info(f"Deleted {deletion_stats['deleted_items']['conversations']} conversations and {deletion_stats['deleted_items']['messages']} messages")
            
            # 2. Delete all documents and chunk details
            documents = await Document.find(Document.user_id == user_id).to_list()
            for document in documents:
                # Delete document chunks
                document_chunks = await DocumentChunk.find(DocumentChunk.document_id == str(document.id)).to_list()
                for document_chunk in document_chunks:
                    await document_chunk.delete()
                    deletion_stats["deleted_items"]["chunk_details"] += 1
                
                # Delete the document
                await document.delete()
                deletion_stats["deleted_items"]["documents"] += 1
            
            logger.info(f"Deleted {deletion_stats['deleted_items']['documents']} documents and {deletion_stats['deleted_items']['chunk_details']} chunk details")
            
            # 3. Delete all vectors from Pinecone
            try:
                await self.pinecone.initialize()
                if self.pinecone.index:
                    pinecone_stats = await self._delete_user_vectors_from_pinecone(user_id)
                    deletion_stats["deleted_items"]["pinecone_vectors"] = pinecone_stats.get("deleted_vectors", 0)
                    logger.info(f"Deleted {pinecone_stats.get('deleted_vectors', 0)} vectors from Pinecone")
                else:
                    logger.warning("Pinecone index not available - skipping vector deletion")
                    deletion_stats["pinecone_warning"] = "Pinecone index not available"
            except Exception as e:
                logger.warning(f"Failed to delete Pinecone vectors: {e}")
                deletion_stats["pinecone_warning"] = f"Pinecone cleanup failed: {str(e)}"
            
            # 4. Finally, delete the user record
            await user.delete()
            logger.info(f"Deleted user record: {user_id}")
            
            deletion_stats["success"] = True
            deletion_stats["message"] = "User profile and all associated data deleted successfully"
            
            logger.info(f"Comprehensive deletion completed for user: {user_id}")
            return deletion_stats
            
        except Exception as e:
            logger.error(f"Failed to delete user profile {user_id}: {e}")
            return {
                "success": False,
                "error": f"Deletion failed: {str(e)}",
                "deleted_items": deletion_stats.get("deleted_items", {})
            }
    
    async def _delete_user_vectors_from_pinecone(self, user_id: str) -> Dict[str, Any]:
        """
        Delete all vectors belonging to a user from Pinecone.
        
        Args:
            user_id: The user ID whose vectors to delete
            
        Returns:
            Dict with deletion statistics
        """
        try:
            # Get the Pinecone index
            index = self.pinecone.index
            if not index:
                return {"deleted_vectors": 0, "error": "Pinecone index not available"}
            
            # Search for all vectors belonging to this user
            # We'll use a broad search to find all user vectors
            search_results = await index.query(
                vector=[0.0] * 1536,  # Dummy vector for search
                top_k=10000,  # Large number to get all vectors
                include_metadata=True,
                filter={"user_id": user_id}
            )
            
            if not search_results.matches:
                return {"deleted_vectors": 0, "message": "No vectors found for user"}
            
            # Extract vector IDs to delete
            vector_ids = [match.id for match in search_results.matches]
            
            # Delete vectors in batches (Pinecone has batch size limits)
            batch_size = 1000
            deleted_count = 0
            
            for i in range(0, len(vector_ids), batch_size):
                batch_ids = vector_ids[i:i + batch_size]
                
                # Delete this batch
                delete_response = await index.delete(ids=batch_ids)
                deleted_count += len(batch_ids)
                
                logger.info(f"Deleted batch {i//batch_size + 1}: {len(batch_ids)} vectors")
            
            return {
                "deleted_vectors": deleted_count,
                "message": f"Successfully deleted {deleted_count} vectors from Pinecone"
            }
            
        except Exception as e:
            logger.error(f"Failed to delete Pinecone vectors for user {user_id}: {e}")
            return {
                "deleted_vectors": 0,
                "error": f"Pinecone deletion failed: {str(e)}"
            }


# Global delete service instance
user_delete_service = UserDeleteService()
