#!/usr/bin/env python3
"""
User-Specific MongoDB Data Cleanup Script
This allows you to clear data for a specific user only.
"""
import asyncio
import os
import sys
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.config import settings
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.db.mongodb_models import User, Conversation, Message, Document, DocumentChunk

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserMongoDBCleanup:
    """User-specific MongoDB data cleanup utility."""
    
    def __init__(self):
        self.database_name = settings.DATABASE_NAME
        
    async def initialize(self):
        """Initialize MongoDB connection."""
        try:
            await connect_to_mongo()
            logger.info("✅ MongoDB connected successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            return False
    
    async def get_user_stats(self, user_id: str):
        """Get statistics for a specific user."""
        try:
            stats = {}
            
            # Count user's documents in each collection
            stats['conversations'] = await Conversation.find(Conversation.user_id == user_id).count()
            stats['documents'] = await Document.find(Document.user_id == user_id).count()
            stats['document_chunks'] = await DocumentChunk.find(DocumentChunk.user_id == user_id).count()
            
            # Get user's conversations to count messages
            user_conversations = await Conversation.find(Conversation.user_id == user_id).to_list()
            conversation_ids = [str(conv.id) for conv in user_conversations]
            
            if conversation_ids:
                stats['messages'] = await Message.find(Message.conversation_id.in_(conversation_ids)).count()
            else:
                stats['messages'] = 0
            
            # Calculate totals
            stats['total_documents'] = sum(stats.values())
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Failed to get user stats: {e}")
            return {}
    
    async def clear_user_data(self, user_id: str):
        """Clear all data for a specific user."""
        try:
            cleared_counts = {}
            
            # Get user's conversations first
            user_conversations = await Conversation.find(Conversation.user_id == user_id).to_list()
            conversation_ids = [str(conv.id) for conv in user_conversations]
            
            # Clear collections in order (respecting foreign key relationships)
            logger.info(f"🗑️  Clearing DocumentChunks for user {user_id}...")
            cleared_counts['document_chunks'] = await DocumentChunk.find(
                DocumentChunk.user_id == user_id
            ).delete()
            
            logger.info(f"🗑️  Clearing Messages for user {user_id}...")
            if conversation_ids:
                cleared_counts['messages'] = await Message.find(
                    Message.conversation_id.in_(conversation_ids)
                ).delete()
            else:
                cleared_counts['messages'] = 0
            
            logger.info(f"🗑️  Clearing Conversations for user {user_id}...")
            cleared_counts['conversations'] = await Conversation.find(
                Conversation.user_id == user_id
            ).delete()
            
            logger.info(f"🗑️  Clearing Documents for user {user_id}...")
            cleared_counts['documents'] = await Document.find(
                Document.user_id == user_id
            ).delete()
            
            return cleared_counts
            
        except Exception as e:
            logger.error(f"❌ Failed to clear user data: {e}")
            return {}
    
    async def list_all_users(self):
        """List all users who have data in the database."""
        try:
            # Get all users
            users = await User.find_all().to_list()
            
            if not users:
                logger.info("ℹ️  No users found in database")
                return []
            
            # Get stats for each user
            user_stats = []
            for user in users:
                stats = await self.get_user_stats(str(user.id))
                user_stats.append({
                    'user_id': str(user.id),
                    'email': user.email,
                    'role': user.role,
                    'total_documents': stats.get('total_documents', 0),
                    'conversations': stats.get('conversations', 0),
                    'messages': stats.get('messages', 0),
                    'documents': stats.get('documents', 0),
                    'document_chunks': stats.get('document_chunks', 0)
                })
            
            return user_stats
            
        except Exception as e:
            logger.error(f"❌ Failed to list users: {e}")
            return []


async def main():
    """Main cleanup function."""
    print("=" * 60)
    print("🧹 User-Specific MongoDB Data Cleanup")
    print("=" * 60)
    
    # Initialize cleanup utility
    cleanup = UserMongoDBCleanup()
    
    # Initialize MongoDB
    if not await cleanup.initialize():
        print("❌ Failed to initialize MongoDB connection")
        return
    
    # List all users
    print("\n📋 Available users:")
    users = await cleanup.list_all_users()
    if not users:
        print("ℹ️  No users found in database")
        return
    
    for i, user in enumerate(users, 1):
        print(f"   {i}. {user['email']} (ID: {user['user_id']}) - {user['total_documents']} documents")
    
    # Get user selection
    print(f"\nDatabase: {settings.DATABASE_NAME}")
    user_input = input("Enter user ID or email to clear data for: ").strip()
    
    if not user_input:
        print("❌ User identifier cannot be empty")
        return
    
    # Find user by ID or email
    selected_user = None
    for user in users:
        if user['user_id'] == user_input or user['email'] == user_input:
            selected_user = user
            break
    
    if not selected_user:
        print(f"❌ User '{user_input}' not found")
        return
    
    # Show user stats
    print(f"\n📊 User Statistics:")
    print(f"   Email: {selected_user['email']}")
    print(f"   Role: {selected_user['role']}")
    print(f"   Conversations: {selected_user['conversations']}")
    print(f"   Messages: {selected_user['messages']}")
    print(f"   Documents: {selected_user['documents']}")
    print(f"   Document Chunks: {selected_user['document_chunks']}")
    print(f"   Total Documents: {selected_user['total_documents']}")
    
    if selected_user['total_documents'] == 0:
        print("\nℹ️  User has no data to clear")
        return
    
    # Safety confirmation
    print(f"\n⚠️  WARNING: This will DELETE ALL DATA for user '{selected_user['email']}'!")
    confirm = input("Type 'YES' to continue: ")
    if confirm != "YES":
        print("❌ Operation cancelled by user")
        return
    
    # Clear user data
    print(f"\n🗑️  Clearing data for user {selected_user['email']}...")
    cleared_counts = await cleanup.clear_user_data(selected_user['user_id'])
    if not cleared_counts:
        print(f"❌ Failed to clear data for user {selected_user['email']}")
        return
    
    print("✅ User data cleared successfully")
    for collection, count in cleared_counts.items():
        print(f"   {collection}: {count} documents deleted")
    
    print("\n" + "=" * 60)
    print("🎉 User data cleanup completed!")
    print("=" * 60)


async def cleanup_and_exit():
    """Cleanup function to close MongoDB connection."""
    try:
        await close_mongo_connection()
    except:
        pass

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Close MongoDB connection
        asyncio.run(cleanup_and_exit())
