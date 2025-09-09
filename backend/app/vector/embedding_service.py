import google.generativeai as genai
from typing import List, Dict, Any
import asyncio
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating embeddings using Gemini."""
    
    def __init__(self):
        self.model = None
        self.embedding_model = None
        
    async def initialize(self):
        """Initialize Gemini models."""
        try:
            # Configure Gemini
            genai.configure(api_key=settings.GEMINI_API_KEY)
            
            # Initialize models
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
            self.embedding_model = genai.embed_content
            
            logger.info("Gemini models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini models: {e}")
            raise
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        try:
            if not self.embedding_model:
                await self.initialize()
            
            # Generate embedding using Gemini
            result = self.embedding_model(
                model=settings.GEMINI_EMBEDDING_MODEL,
                content=text,
                task_type="retrieval_document"
            )
            
            return result['embedding']
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise
    
    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        try:
            if not self.embedding_model:
                await self.initialize()
            
            embeddings = []
            
            # Process in batches to avoid rate limits
            batch_size = 10
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                
                # Generate embeddings for batch
                batch_embeddings = []
                for text in batch_texts:
                    embedding = await self.generate_embedding(text)
                    batch_embeddings.append(embedding)
                
                embeddings.extend(batch_embeddings)
                
                # Small delay between batches
                if i + batch_size < len(texts):
                    await asyncio.sleep(0.1)
            
            logger.info(f"Generated {len(embeddings)} embeddings")
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {e}")
            raise
    
    async def generate_query_embedding(self, query: str) -> List[float]:
        """Generate embedding for a query (optimized for retrieval)."""
        try:
            if not self.embedding_model:
                await self.initialize()
            
            # Generate embedding with query task type using Gemini
            result = self.embedding_model(
                model=settings.GEMINI_EMBEDDING_MODEL,
                content=query,
                task_type="retrieval_query"
            )
            
            return result['embedding']
            
        except Exception as e:
            logger.error(f"Failed to generate query embedding: {e}")
            raise


# Global embedding service instance
embedding_service = EmbeddingService()
