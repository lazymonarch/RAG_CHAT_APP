from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.core.config import settings
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.auth.routes import router as auth_router
from app.users.routes import router as users_router
from app.documents.routes import router as documents_router
from app.chat.routes import router as chat_router
from app.vector.vector_service import vector_service
from app.chat.service import openai_chat_service
from app.vector.pinecone_client import pinecone_client

# Setup logging
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="A RAG-powered chat application with document processing and AI responses",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(documents_router)
app.include_router(chat_router)


@app.on_event("startup")
async def startup_event():
    """Initialize database connection and services on startup."""
    # Initialize database
    await connect_to_mongo()
    
    # Initialize vector services
    try:
        await pinecone_client.initialize()
        await vector_service.initialize()
        await openai_chat_service.initialize()
        logger.info("✅ All services initialized successfully")
    except Exception as e:
        logger.warning(f"⚠️ Service initialization warning: {e}")
        # Continue startup even if some services fail


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown."""
    await close_mongo_connection()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to RAG Chat Application",
        "version": settings.VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": settings.VERSION}
