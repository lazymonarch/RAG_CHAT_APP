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
        """Generate embeddings for multiple texts with proper batching."""
        try:
            if not self.client:
                await self.initialize()
            
            # Validate and clean input texts
            if not texts:
                raise ValueError("No texts provided for embedding")
            
            # Filter out empty or whitespace-only texts
            valid_texts = []
            for i, text in enumerate(texts):
                if text and text.strip():
                    # Ensure text is not too long (OpenAI has limits)
                    if len(text) > 8000:  # Conservative limit
                        logger.warning(f"Text {i} is too long ({len(text)} chars), truncating")
                        text = text[:8000]
                    valid_texts.append(text.strip())
                else:
                    logger.warning(f"Skipping empty text at index {i}")
            
            if not valid_texts:
                raise ValueError("No valid texts found for embedding")
            
            logger.info(f"Generating embeddings for {len(valid_texts)} texts")
            
            # Process in batches to avoid API limits
            # OpenAI has a limit of 2048 inputs per request
            batch_size = 1000  # Conservative batch size
            all_embeddings = []
            
            for i in range(0, len(valid_texts), batch_size):
                batch_texts = valid_texts[i:i + batch_size]
                logger.info(f"Processing batch {i//batch_size + 1}/{(len(valid_texts) + batch_size - 1)//batch_size} ({len(batch_texts)} texts)")
                
                try:
                    # Generate embeddings for this batch
                    response = await self.client.embeddings.create(
                        model=self.embedding_model,
                        input=batch_texts,
                        encoding_format="float"
                    )
                    
                    batch_embeddings = [data.embedding for data in response.data]
                    all_embeddings.extend(batch_embeddings)
                    
                    # Small delay between batches to avoid rate limiting
                    if i + batch_size < len(valid_texts):
                        await asyncio.sleep(0.1)
                        
                except Exception as batch_error:
                    logger.error(f"Failed to process batch {i//batch_size + 1}: {batch_error}")
                    # Continue with next batch instead of failing completely
                    continue
            
            if not all_embeddings:
                raise ValueError("No embeddings generated from any batch")
            
            logger.info(f"Successfully generated {len(all_embeddings)} embeddings")
            return all_embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {e}")
            logger.error(f"Input texts count: {len(texts) if texts else 0}")
            if texts:
                logger.error(f"First text sample: {texts[0][:100] if texts[0] else 'Empty'}")
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
