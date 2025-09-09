import pinecone
from pinecone import Pinecone, ServerlessSpec
from typing import List, Dict, Any, Optional
import asyncio
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class PineconeClient:
    """Pinecone client for vector operations."""
    
    def __init__(self):
        self.pc = None
        self.index = None
        self.index_name = settings.PINECONE_INDEX_NAME
        self.dimension = settings.EMBEDDING_DIMENSION
        
    async def initialize(self):
        """Initialize Pinecone client and connect to index."""
        try:
            # Initialize Pinecone
            self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
            
            # Check if index exists, create if not
            if self.index_name not in self.pc.list_indexes().names():
                logger.info(f"Creating Pinecone index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
                # Wait for index to be ready
                await asyncio.sleep(10)
            else:
                # Check if existing index has correct dimension
                existing_index = self.pc.describe_index(self.index_name)
                if existing_index.dimension != self.dimension:
                    logger.warning(f"Index dimension mismatch. Expected {self.dimension}, got {existing_index.dimension}")
                    logger.info("Deleting existing index and creating new one...")
                    self.pc.delete_index(self.index_name)
                    await asyncio.sleep(5)
                    self.pc.create_index(
                        name=self.index_name,
                        dimension=self.dimension,
                        metric="cosine",
                        spec=ServerlessSpec(
                            cloud="aws",
                            region="us-east-1"
                        )
                    )
                    await asyncio.sleep(10)
            
            # Connect to index
            self.index = self.pc.Index(self.index_name)
            logger.info(f"Connected to Pinecone index: {self.index_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {e}")
            raise
    
    async def upsert_vectors(self, vectors: List[Dict[str, Any]]) -> bool:
        """Upsert vectors to Pinecone index."""
        try:
            if not self.index:
                await self.initialize()
            
            # Prepare vectors for upsert
            upsert_vectors = []
            for vector_data in vectors:
                upsert_vectors.append({
                    "id": vector_data["id"],
                    "values": vector_data["values"],
                    "metadata": vector_data.get("metadata", {})
                })
            
            # Upsert in batches
            batch_size = 100
            for i in range(0, len(upsert_vectors), batch_size):
                batch = upsert_vectors[i:i + batch_size]
                self.index.upsert(vectors=batch)
            
            logger.info(f"Successfully upserted {len(vectors)} vectors")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upsert vectors: {e}")
            return False
    
    async def query_vectors(
        self, 
        query_vector: List[float], 
        top_k: int = None,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Query vectors from Pinecone index."""
        try:
            if not self.index:
                await self.initialize()
            
            top_k = top_k or settings.TOP_K_RESULTS
            
            # Prepare query
            query_params = {
                "vector": query_vector,
                "top_k": top_k,
                "include_metadata": True
            }
            
            if filter_dict:
                query_params["filter"] = filter_dict
            
            # Execute query
            results = self.index.query(**query_params)
            
            # Format results
            formatted_results = []
            for match in results.matches:
                formatted_results.append({
                    "id": match.id,
                    "score": match.score,
                    "metadata": match.metadata
                })
            
            logger.info(f"Retrieved {len(formatted_results)} vectors from query")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to query vectors: {e}")
            return []
    
    async def delete_vectors(self, vector_ids: List[str]) -> bool:
        """Delete vectors from Pinecone index."""
        try:
            if not self.index:
                await self.initialize()
            
            self.index.delete(ids=vector_ids)
            logger.info(f"Successfully deleted {len(vector_ids)} vectors")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete vectors: {e}")
            return False
    
    async def get_index_stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        try:
            if not self.index:
                await self.initialize()
            
            stats = self.index.describe_index_stats()
            return {
                "total_vector_count": stats.total_vector_count,
                "dimension": stats.dimension,
                "index_fullness": stats.index_fullness
            }
            
        except Exception as e:
            logger.error(f"Failed to get index stats: {e}")
            return {}


# Global Pinecone client instance
pinecone_client = PineconeClient()
