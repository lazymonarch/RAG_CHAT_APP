from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Dict, Any
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class TextChunker:
    """Service for chunking text into smaller pieces for embedding."""
    
    def __init__(self):
        self.text_splitter = None
        
    def initialize(self):
        """Initialize text splitter."""
        try:
            # Initialize text splitter with character-based chunking
            # Use larger chunks to reduce total number of chunks
            effective_chunk_size = max(settings.CHUNK_SIZE, 1000)  # Minimum 1000 chars
            effective_overlap = min(settings.CHUNK_OVERLAP, 200)   # Maximum 200 chars overlap
            
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=effective_chunk_size,
                chunk_overlap=effective_overlap,
                length_function=len,  # Use character count
                separators=["\n\n", "\n", ". ", " ", ""]  # Better separators for larger chunks
            )
            
            logger.info("Text chunker initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize text chunker: {e}")
            raise
    
    def count_tokens(self, text: str) -> int:
        """Estimate token count using character-based approximation."""
        try:
            # Rough approximation: 1 token ≈ 4 characters for English text
            # This is a conservative estimate for Gemini models
            return len(text) // 4
            
        except Exception as e:
            logger.error(f"Failed to count tokens: {e}")
            return len(text.split())  # Fallback to word count
    
    def chunk_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Chunk text into smaller pieces with metadata."""
        try:
            if not self.text_splitter:
                self.initialize()
            
            # Validate input text
            if not text or not text.strip():
                logger.warning("Empty or whitespace-only text provided for chunking")
                return []
            
            # Split text into chunks
            chunks = self.text_splitter.split_text(text)
            
            # Filter out empty chunks
            valid_chunks = [chunk for chunk in chunks if chunk and chunk.strip()]
            
            if not valid_chunks:
                logger.warning("No valid chunks created from text")
                return []
            
            # Create chunk metadata
            chunk_metadata = metadata or {}
            chunked_texts = []
            
            for i, chunk in enumerate(valid_chunks):
                chunk_data = {
                    "text": chunk.strip(),
                    "chunk_index": i,
                    "token_count": self.count_tokens(chunk),
                    "metadata": {
                        **chunk_metadata,
                        "chunk_index": i,
                        "total_chunks": len(valid_chunks)
                    }
                }
                chunked_texts.append(chunk_data)
            
            logger.info(f"Created {len(chunked_texts)} valid chunks from text")
            return chunked_texts
            
        except Exception as e:
            logger.error(f"Failed to chunk text: {e}")
            return []
    
    def chunk_document(self, content: str, document_metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Chunk a document with proper metadata."""
        try:
            # Add document metadata to each chunk
            chunk_metadata = {
                "document_id": document_metadata.get("document_id"),
                "user_id": document_metadata.get("user_id"),
                "filename": document_metadata.get("filename"),
                "file_type": document_metadata.get("file_type"),
                "upload_timestamp": document_metadata.get("upload_timestamp")
            }
            
            chunks = self.chunk_text(content, chunk_metadata)
            
            # Add chunk-specific metadata
            for i, chunk in enumerate(chunks):
                chunk["metadata"]["chunk_id"] = f"{document_metadata.get('document_id')}_chunk_{i}"
                chunk["metadata"]["is_first_chunk"] = (i == 0)
                chunk["metadata"]["is_last_chunk"] = (i == len(chunks) - 1)
            
            return chunks
            
        except Exception as e:
            logger.error(f"Failed to chunk document: {e}")
            return []


# Global text chunker instance
text_chunker = TextChunker()
