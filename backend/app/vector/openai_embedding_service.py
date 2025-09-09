import openai
from typing import List, Dict, Any
import asyncio
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class OpenAIEmbeddingService:
    """OpenAI embedding service for generating text embeddings."""
    
    def __init__(self):
        self.client = None
        self.embedding_model = settings.OPENAI_EMBEDDING_MODEL
        
    async def initialize(self):
        """Initialize OpenAI client."""
        try:
            self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            logger.info("OpenAI embedding service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        try:
            if not self.client:
                await self.initialize()
            
            # Generate embedding using OpenAI
            response = await self.client.embeddings.create(
                model=self.embedding_model,
                input=text,
                encoding_format="float"
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise
    
    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        try:
            if not self.client:
                await self.initialize()
            
            # Generate embeddings in batch
            response = await self.client.embeddings.create(
                model=self.embedding_model,
                input=texts,
                encoding_format="float"
            )
            
            return [data.embedding for data in response.data]
            
        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {e}")
            raise
    
    async def generate_query_embedding(self, query: str) -> List[float]:
        """Generate embedding for a query (optimized for retrieval)."""
        try:
            if not self.client:
                await self.initialize()
            
            # Generate embedding for query
            response = await self.client.embeddings.create(
                model=self.embedding_model,
                input=query,
                encoding_format="float"
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Failed to generate query embedding: {e}")
            raise


# Global embedding service instance
openai_embedding_service = OpenAIEmbeddingService()
