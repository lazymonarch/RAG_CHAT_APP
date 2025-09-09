from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Project Configuration
    PROJECT_NAME: str = "RAG Chat Application"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # MongoDB Configuration
    MONGODB_URL: str
    DATABASE_NAME: str = "rag_chat_app"
    
    # Authentication
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # OpenAI API Configuration
    OPENAI_API_KEY: str
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_LLM_MODEL: str = "gpt-4o-mini"
    
    # Pinecone Configuration
    PINECONE_API_KEY: str
    PINECONE_PROJECT_NAME: str = "rag-chat-app"
    PINECONE_INDEX_NAME: str = "rag-chat-embeddings"
    
    # RAG Configuration
    CHUNK_SIZE: int = 600
    CHUNK_OVERLAP: int = 100
    TOP_K_RESULTS: int = 6
    EMBEDDING_DIMENSION: int = 1536  # text-embedding-3-small dimension
    
    # File Upload Configuration
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_FILE_TYPES: str = "pdf,txt,docx,doc"
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # LLM Configuration
    MAX_OUTPUT_TOKENS: int = 500   # Maximum response length for RAG
    TEMPERATURE: float = 0.1       # Low temperature for factual responses
    TOP_P: float = 1.0            # Nucleus sampling
    FREQUENCY_PENALTY: float = 0.1 # Reduce repetition
    PRESENCE_PENALTY: float = 0.1  # Encourage diverse responses
    STREAMING: bool = False       # Disable streaming for simplicity
    
    @property
    def allowed_file_types_list(self) -> List[str]:
        """Get allowed file types as a list."""
        return [file_type.strip() for file_type in self.ALLOWED_FILE_TYPES.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()
