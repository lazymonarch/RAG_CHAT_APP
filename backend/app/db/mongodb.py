from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.core.config import settings
from app.db.mongodb_models import User, Conversation, Message, Document, DocumentChunk


class Database:
    client: AsyncIOMotorClient = None
    database = None


db = Database()


async def connect_to_mongo():
    """Create database connection."""
    db.client = AsyncIOMotorClient(settings.MONGODB_URL)
    db.database = db.client[settings.DATABASE_NAME]
    
    # Initialize Beanie with the document models
    await init_beanie(
        database=db.database,
        document_models=[User, Conversation, Message, Document, DocumentChunk]
    )


async def close_mongo_connection():
    """Close database connection."""
    if db.client:
        db.client.close()
