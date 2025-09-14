"""
Frontend Configuration
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Backend API Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Streamlit Configuration
STREAMLIT_SERVER_PORT = int(os.getenv("STREAMLIT_SERVER_PORT", "8501"))
STREAMLIT_SERVER_ADDRESS = os.getenv("STREAMLIT_SERVER_ADDRESS", "0.0.0.0")

# App Configuration
APP_TITLE = os.getenv("APP_TITLE", "RAG Chat Application")
APP_ICON = os.getenv("APP_ICON", "🤖")
APP_LAYOUT = os.getenv("APP_LAYOUT", "wide")
APP_SIDEBAR_STATE = os.getenv("APP_SIDEBAR_STATE", "expanded")

# Chat Configuration
MAX_MESSAGE_HISTORY = int(os.getenv("MAX_MESSAGE_HISTORY", "50"))
AUTO_REFRESH_INTERVAL = int(os.getenv("AUTO_REFRESH_INTERVAL", "5"))

# File Upload Configuration
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
ALLOWED_FILE_TYPES = os.getenv("ALLOWED_FILE_TYPES", "pdf,txt,docx,doc").split(",")

# API Endpoints
AUTH_ENDPOINTS = {
    "login": f"{API_BASE_URL}/auth/login",
    "register": f"{API_BASE_URL}/auth/register"
}

USER_ENDPOINTS = {
    "me": f"{API_BASE_URL}/users/me",
    "list": f"{API_BASE_URL}/users/"
}

DOCUMENT_ENDPOINTS = {
    "upload": f"{API_BASE_URL}/documents/upload",
    "list": f"{API_BASE_URL}/documents/",
    "get": f"{API_BASE_URL}/documents/",
    "delete": f"{API_BASE_URL}/documents/"
}

CHAT_ENDPOINTS = {
    "query": f"{API_BASE_URL}/chat/query",
    "history": f"{API_BASE_URL}/chat/history",
    "conversation": f"{API_BASE_URL}/chat/conversation/"
}
