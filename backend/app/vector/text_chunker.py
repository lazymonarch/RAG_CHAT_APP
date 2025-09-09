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
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=settings.CHUNK_SIZE,
                chunk_overlap=settings.CHUNK_OVERLAP,
                length_function=len,  # Use character count
                separators=["\n\n", "\n", " ", ""]
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
            
            # Split text into chunks
            chunks = self.text_splitter.split_text(text)
            
            # Create chunk metadata
            chunk_metadata = metadata or {}
            chunked_texts = []
            
            for i, chunk in enumerate(chunks):
                chunk_data = {
                    "text": chunk,
                    "chunk_index": i,
                    "token_count": self.count_tokens(chunk),
                    "metadata": {
                        **chunk_metadata,
                        "chunk_index": i,
                        "total_chunks": len(chunks)
                    }
                }
                chunked_texts.append(chunk_data)
            
            logger.info(f"Created {len(chunked_texts)} chunks from text")
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
