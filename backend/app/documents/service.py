import os
import io
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
import PyPDF2
from docx import Document
from app.core.config import settings
from app.db.mongodb_models import Document as DocumentModel, DocumentChunk
from app.vector.vector_service import vector_service

logger = logging.getLogger(__name__)


class DocumentProcessingService:
    """Service for processing uploaded documents."""
    
    def __init__(self):
        self.upload_dir = "uploads"
        self.max_file_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024  # Convert to bytes
        self.allowed_types = settings.allowed_file_types_list
        
    async def process_document(
        self, 
        file_content: bytes, 
        filename: str, 
        user_id: str
    ) -> Dict[str, Any]:
        """Process uploaded document and store in vector database."""
        try:
            # Validate file
            validation_result = self._validate_file(file_content, filename)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": validation_result["error"],
                    "document_id": None
                }
            
            # Extract text content first
            text_content = await self._extract_text(file_content, filename)
            if not text_content:
                return {
                    "success": False,
                    "error": "Failed to extract text from document",
                    "document_id": None
                }
            
            # Log text extraction details
            logger.info(f"Extracted text length: {len(text_content)} characters")
            
            # Create document record in MongoDB first to get the ID
            document_record = DocumentModel(
                user_id=user_id,
                filename=filename,
                original_filename=filename,
                file_type=self._get_file_extension(filename),
                file_size=len(file_content),
                chunk_count=0,  # Will be updated after processing
                pinecone_ids=[],  # Will be updated after processing
                processing_status="processing"
            )
            
            await document_record.insert()
            document_id = str(document_record.id)
            
            # Create document metadata using MongoDB ObjectId
            document_metadata = {
                "document_id": document_id,
                "user_id": user_id,
                "filename": filename,
                "file_type": self._get_file_extension(filename),
                "file_size": len(file_content),
                "upload_timestamp": datetime.utcnow().isoformat()
            }
            
            # Process with vector service
            vector_result = await vector_service.process_and_store_document(
                content=text_content,
                document_metadata=document_metadata
            )
            
            if not vector_result["success"]:
                # Delete the document record if vector processing failed
                await document_record.delete()
                return {
                    "success": False,
                    "error": f"Vector processing failed: {vector_result['error']}",
                    "document_id": document_id
                }
            
            # Update document record with vector processing results
            document_record.chunk_count = vector_result["chunk_count"]
            document_record.pinecone_ids = vector_result["pinecone_ids"]
            document_record.processing_status = "completed"
            
            await document_record.save()
            
            # Save chunk details to MongoDB
            await self._save_chunk_details(
                document_id=document_id,
                user_id=user_id,
                vector_result=vector_result,
                text_content=text_content,
                filename=filename,
                file_type=self._get_file_extension(filename),
                file_size=len(file_content)
            )
            
            logger.info(f"Document processed successfully: {document_id}")
            
            return {
                "success": True,
                "document_id": document_id,
                "filename": filename,
                "chunk_count": vector_result["chunk_count"],
                "file_size": len(file_content),
                "processing_status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Document processing failed: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e),
                "document_id": document_id if 'document_id' in locals() else None
            }
    
    def _validate_file(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Validate uploaded file."""
        try:
            # Check file size
            if len(file_content) > self.max_file_size:
                return {
                    "valid": False,
                    "error": f"File too large. Maximum size: {settings.MAX_FILE_SIZE_MB}MB"
                }
            
            # Check file type
            file_extension = self._get_file_extension(filename).lower()
            if file_extension not in self.allowed_types:
                return {
                    "valid": False,
                    "error": f"File type not allowed. Allowed types: {', '.join(self.allowed_types)}"
                }
            
            # Check if file is empty
            if len(file_content) == 0:
                return {
                    "valid": False,
                    "error": "File is empty"
                }
            
            return {"valid": True}
            
        except Exception as e:
            return {
                "valid": False,
                "error": f"File validation failed: {str(e)}"
            }
    
    async def _extract_text(self, file_content: bytes, filename: str) -> Optional[str]:
        """Extract text content from document."""
        try:
            file_extension = self._get_file_extension(filename).lower()
            
            if file_extension == "pdf":
                return await self._extract_pdf_text(file_content)
            elif file_extension in ["txt"]:
                return await self._extract_txt_text(file_content)
            elif file_extension in ["docx", "doc"]:
                return await self._extract_docx_text(file_content)
            else:
                logger.error(f"Unsupported file type: {file_extension}")
                return None
                
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            return None
    
    async def _extract_pdf_text(self, file_content: bytes) -> Optional[str]:
        """Extract text from PDF file."""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            text = ""
            
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"PDF text extraction failed: {e}")
            return None
    
    async def _extract_txt_text(self, file_content: bytes) -> Optional[str]:
        """Extract text from TXT file."""
        try:
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            
            for encoding in encodings:
                try:
                    return file_content.decode(encoding).strip()
                except UnicodeDecodeError:
                    continue
            
            # If all encodings fail, use utf-8 with error handling
            return file_content.decode('utf-8', errors='ignore').strip()
            
        except Exception as e:
            logger.error(f"TXT text extraction failed: {e}")
            return None
    
    async def _extract_docx_text(self, file_content: bytes) -> Optional[str]:
        """Extract text from DOCX file."""
        try:
            doc = Document(io.BytesIO(file_content))
            text = ""
            
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"DOCX text extraction failed: {e}")
            return None
    
    def _get_file_extension(self, filename: str) -> str:
        """Get file extension from filename."""
        return os.path.splitext(filename)[1][1:]  # Remove the dot
    
    async def _save_chunk_details(
        self, 
        document_id: str, 
        user_id: str, 
        vector_result: Dict[str, Any],
        text_content: str,
        filename: str,
        file_type: str,
        file_size: int
    ) -> None:
        """Save detailed chunk information to MongoDB."""
        try:
            # Chunk the text to get detailed information
            chunks = vector_service.chunker.chunk_text(text_content)
            
            # Save each chunk detail
            for i, chunk in enumerate(chunks):
                chunk_record = DocumentChunk(
                    document_id=str(document_id),  # Convert ObjectId to string
                    user_id=user_id,
                    chunk_index=i,
                    content=chunk["text"],
                    pinecone_id=vector_result["pinecone_ids"][i] if i < len(vector_result["pinecone_ids"]) else f"{document_id}_chunk_{i}",
                    token_count=chunk["token_count"],
                    filename=filename,
                    original_filename=filename,
                    file_type=file_type,
                    file_size=file_size,
                    chunk_count=len(chunks),
                    pinecone_ids=vector_result["pinecone_ids"]
                )
                
                await chunk_record.insert()
                
        except Exception as e:
            logger.error(f"Failed to save chunk details: {e}")
    
    async def get_user_documents(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all documents for a user."""
        try:
            documents = await DocumentModel.find(
                DocumentModel.user_id == user_id
            ).to_list()
            
            return [
                {
                    "id": str(doc.id),
                    "user_id": doc.user_id,
                    "filename": doc.filename,
                    "original_filename": doc.original_filename,
                    "file_type": doc.file_type,
                    "file_size": doc.file_size,
                    "chunk_count": doc.chunk_count,
                    "upload_timestamp": doc.upload_timestamp,
                    "processing_status": doc.processing_status,
                    "error_message": doc.error_message
                }
                for doc in documents
            ]
            
        except Exception as e:
            logger.error(f"Failed to get user documents: {e}")
            return []
    
    async def delete_document(self, document_id: str, user_id: str) -> Dict[str, Any]:
        """Delete document and its vectors."""
        try:
            # Get document
            document = await DocumentModel.get(document_id)
            if not document or document.user_id != user_id:
                return {
                    "success": False,
                    "error": "Document not found or access denied"
                }
            
            # Delete vectors from Pinecone
            if document.pinecone_ids:
                await vector_service.delete_document_vectors(document.pinecone_ids)
            
            # Delete chunk records
            await DocumentChunk.find(
                DocumentChunk.document_id == document_id
            ).delete()
            
            # Delete document record
            await document.delete()
            
            logger.info(f"Document deleted successfully: {document_id}")
            
            return {
                "success": True,
                "message": "Document deleted successfully"
            }
            
        except Exception as e:
            logger.error(f"Document deletion failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Global document processing service instance
document_service = DocumentProcessingService()
