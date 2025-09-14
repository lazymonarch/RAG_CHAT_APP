"""
API Client for communicating with FastAPI backend
"""
import requests
import streamlit as st
from typing import Dict, List, Optional, Any
import json
from config import (
    AUTH_ENDPOINTS, USER_ENDPOINTS, DOCUMENT_ENDPOINTS, CHAT_ENDPOINTS,
    MAX_FILE_SIZE_MB, ALLOWED_FILE_TYPES
)


class APIClient:
    """Client for communicating with the FastAPI backend."""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.session = requests.Session()
        
    def _get_headers(self, include_auth: bool = True) -> Dict[str, str]:
        """Get request headers with optional authentication."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if include_auth and "access_token" in st.session_state:
            headers["Authorization"] = f"Bearer {st.session_state.access_token}"
        
        return headers
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response and return data or raise error."""
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            error_msg = "API Error"
            try:
                error_data = response.json()
                error_msg = error_data.get("detail", str(e))
            except:
                error_msg = str(e)
            raise Exception(f"{error_msg} (Status: {response.status_code})")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network Error: {str(e)}")
    
    # Authentication Methods
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """Login user and return token."""
        data = {
            "email": email,
            "password": password
        }
        
        response = self.session.post(
            AUTH_ENDPOINTS["login"],
            json=data,
            headers=self._get_headers(include_auth=False)
        )
        
        return self._handle_response(response)
    
    def register(self, email: str, password: str, name: str = None) -> Dict[str, Any]:
        """Register new user."""
        data = {
            "email": email,
            "password": password,
            "name": name
        }
        
        response = self.session.post(
            AUTH_ENDPOINTS["register"],
            json=data,
            headers=self._get_headers(include_auth=False)
        )
        
        return self._handle_response(response)
    
    # User Methods
    def get_current_user(self) -> Dict[str, Any]:
        """Get current user information."""
        response = self.session.get(
            USER_ENDPOINTS["me"],
            headers=self._get_headers()
        )
        
        return self._handle_response(response)
    
    # Document Methods
    def upload_document(self, file, filename: str) -> Dict[str, Any]:
        """Upload document to backend."""
        files = {
            "file": (filename, file, "application/octet-stream")
        }
        
        # Remove Content-Type header for file upload
        headers = self._get_headers()
        headers.pop("Content-Type", None)
        
        response = self.session.post(
            DOCUMENT_ENDPOINTS["upload"],
            files=files,
            headers=headers
        )
        
        return self._handle_response(response)
    
    def get_documents(self) -> List[Dict[str, Any]]:
        """Get user's documents."""
        response = self.session.get(
            DOCUMENT_ENDPOINTS["list"],
            headers=self._get_headers()
        )
        
        data = self._handle_response(response)
        return data.get("documents", [])
    
    def delete_document(self, document_id: str) -> Dict[str, Any]:
        """Delete document."""
        response = self.session.delete(
            f"{DOCUMENT_ENDPOINTS['delete']}{document_id}",
            headers=self._get_headers()
        )
        
        return self._handle_response(response)
    
    # Chat Methods
    def start_conversation(self) -> Dict[str, Any]:
        """Start a new conversation."""
        response = self.session.post(
            f"{self.base_url}/chat/start",
            headers=self._get_headers()
        )
        
        return self._handle_response(response)
    
    def send_message(self, conversation_id: str, message: str) -> Dict[str, Any]:
        """Send message to a conversation."""
        data = {
            "content": message
        }
        
        response = self.session.post(
            f"{self.base_url}/chat/{conversation_id}/query",
            json=data,
            headers=self._get_headers()
        )
        
        return self._handle_response(response)
    
    def get_chat_history(self) -> List[Dict[str, Any]]:
        """Get chat history."""
        response = self.session.get(
            f"{self.base_url}/chat/history",
            headers=self._get_headers()
        )
        
        return self._handle_response(response)
    
    def get_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """Get specific conversation with messages."""
        response = self.session.get(
            f"{self.base_url}/chat/{conversation_id}",
            headers=self._get_headers()
        )
        
        return self._handle_response(response)
    
    def delete_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """Delete a conversation."""
        response = self.session.delete(
            f"{self.base_url}/chat/{conversation_id}",
            headers=self._get_headers()
        )
        
        return self._handle_response(response)
    
    def test_chat(self, message: str) -> Dict[str, Any]:
        """Test chat without RAG."""
        data = {
            "content": message
        }
        
        response = self.session.post(
            f"{self.base_url}/chat/test",
            json=data,
            headers=self._get_headers()
        )
        
        return self._handle_response(response)
    
    # Profile Methods
    def get_user_profile(self) -> Dict[str, Any]:
        """Get user profile with statistics."""
        response = self.session.get(
            f"{self.base_url}/users/me/profile",
            headers=self._get_headers()
        )
        
        return self._handle_response(response)
    
    # Document Chat Methods
    def get_selectable_documents(self) -> List[Dict[str, Any]]:
        """Get documents available for document chat."""
        response = self.session.get(
            f"{self.base_url}/chat/documents/selectable",
            headers=self._get_headers()
        )
        
        return self._handle_response(response)
    
    def start_document_conversation(self, document_ids: List[str]) -> Dict[str, Any]:
        """Start a new document-scoped conversation."""
        data = {
            "document_ids": document_ids
        }
        
        response = self.session.post(
            f"{self.base_url}/chat/start-document",
            json=data,
            headers=self._get_headers()
        )
        
        return self._handle_response(response)
    
    # Utility Methods
    def validate_file(self, file) -> tuple[bool, str]:
        """Validate uploaded file."""
        if file is None:
            return False, "No file selected"
        
        # Check file size
        file_size_mb = len(file.getvalue()) / (1024 * 1024)
        if file_size_mb > MAX_FILE_SIZE_MB:
            return False, f"File size ({file_size_mb:.1f}MB) exceeds limit ({MAX_FILE_SIZE_MB}MB)"
        
        # Check file type
        file_extension = file.name.split('.')[-1].lower()
        if file_extension not in ALLOWED_FILE_TYPES:
            return False, f"File type '{file_extension}' not allowed. Allowed: {', '.join(ALLOWED_FILE_TYPES)}"
        
        return True, "File is valid"
    
    def email_chat_summary(self, conversation_id: str) -> Dict[str, Any]:
        """Send chat summary via email."""
        response = self.session.post(
            f"{self.base_url}/chat/{conversation_id}/email",
            headers=self._get_headers()
        )
        return self._handle_response(response)


# Global API client instance
api_client = APIClient()
