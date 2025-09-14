from typing import List, Dict, Any, Optional
import logging
from app.vector.pinecone_client import pinecone_client
from app.vector.openai_embedding_service import openai_embedding_service
from app.vector.text_chunker import text_chunker
from app.core.config import settings

logger = logging.getLogger(__name__)


class VectorService:
    """Main service for vector operations combining Pinecone, embeddings, and chunking."""
    
    def __init__(self):
        self.pinecone = pinecone_client
        self.embeddings = openai_embedding_service
        self.chunker = text_chunker
        
    async def initialize(self):
        """Initialize all vector services."""
        try:
            await self.pinecone.initialize()
            await self.embeddings.initialize()
            self.chunker.initialize()
            logger.info("Vector service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize vector service: {e}")
            raise
    
    async def process_and_store_document(
        self, 
        content: str, 
        document_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process document content and store in vector database."""
        try:
            # Chunk the document
            chunks = self.chunker.chunk_document(content, document_metadata)
            
            if not chunks:
                raise ValueError("No chunks created from document")
            
            # Generate embeddings for all chunks
            texts = [chunk["text"] for chunk in chunks]
            embeddings = await self.embeddings.generate_embeddings_batch(texts)
            
            # Prepare vectors for Pinecone
            vectors = []
            pinecone_ids = []
            
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                vector_id = f"{document_metadata['document_id']}_chunk_{i}"
                pinecone_ids.append(vector_id)
                
                vector_data = {
                    "id": vector_id,
                    "values": embedding,
                    "metadata": {
                        **chunk["metadata"],
                        "text": chunk["text"]  # Include text content in metadata
                    }
                }
                vectors.append(vector_data)
            
            # Store in Pinecone
            success = await self.pinecone.upsert_vectors(vectors)
            
            if not success:
                raise ValueError("Failed to store vectors in Pinecone")
            
            return {
                "success": True,
                "chunk_count": len(chunks),
                "pinecone_ids": pinecone_ids,
                "document_id": document_metadata["document_id"]
            }
            
        except Exception as e:
            logger.error(f"Failed to process and store document: {e}")
            return {
                "success": False,
                "error": str(e),
                "chunk_count": 0,
                "pinecone_ids": []
            }
    
    async def search_similar_content(
        self, 
        query: str, 
        user_id: str,
        top_k: int = None
    ) -> List[Dict[str, Any]]:
        """Search for similar content using vector similarity."""
        try:
            # Generate query embedding
            query_embedding = await self.embeddings.generate_query_embedding(query)
            
            # Create filter for user-specific content
            filter_dict = {"user_id": user_id}
            
            # Search in Pinecone
            results = await self.pinecone.query_vectors(
                query_vector=query_embedding,
                top_k=top_k or settings.TOP_K_RESULTS,
                filter_dict=filter_dict
            )
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "id": result["id"],
                    "score": result["score"],
                    "text": result["metadata"].get("text", ""),
                    "metadata": result["metadata"]
                })
            
            logger.info(f"Found {len(formatted_results)} similar content pieces")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to search similar content: {e}")
            return []
    
    async def search_document_scoped_content(
        self, 
        query: str, 
        user_id: str,
        document_ids: List[str],
        top_k: int = None
    ) -> List[Dict[str, Any]]:
        """Search for similar content within specific documents."""
        try:
            # Generate query embedding
            query_embedding = await self.embeddings.generate_query_embedding(query)
            
            # Create filter for user-specific content and document scope
            filter_dict = {
                "user_id": user_id,
                "document_id": {"$in": document_ids}
            }
            
            # Search in Pinecone
            results = await self.pinecone.query_vectors(
                query_vector=query_embedding,
                top_k=top_k or settings.TOP_K_RESULTS,
                filter_dict=filter_dict
            )
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "id": result["id"],
                    "score": result["score"],
                    "text": result["metadata"].get("text", ""),
                    "metadata": result["metadata"]
                })
            
            logger.info(f"Found {len(formatted_results)} similar content pieces in {len(document_ids)} documents")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to search document-scoped content: {e}")
            return []
    
    async def delete_document_vectors(self, pinecone_ids: List[str]) -> bool:
        """Delete all vectors for a document."""
        try:
            success = await self.pinecone.delete_vectors(pinecone_ids)
            logger.info(f"Deleted {len(pinecone_ids)} vectors for document")
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete document vectors: {e}")
            return False
    
    async def get_vector_stats(self) -> Dict[str, Any]:
        """Get vector database statistics."""
        try:
            stats = await self.pinecone.get_index_stats()
            return {
                "vector_count": stats.get("total_vector_count", 0),
                "dimension": stats.get("dimension", 0),
                "index_fullness": stats.get("index_fullness", 0)
            }
            
        except Exception as e:
            logger.error(f"Failed to get vector stats: {e}")
            return {}


# Global vector service instance
vector_service = VectorService()
