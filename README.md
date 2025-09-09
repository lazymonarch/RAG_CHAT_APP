# RAG Chat Application

A real-world chat application demonstrating LLM, RAG, and modern frameworks.

## 🏗️ Project Structure

```
RAG_CHAT_APP/
├── backend/                 # FastAPI Backend
│   ├── app/                # Main application code
│   │   ├── auth/           # Authentication routes
│   │   ├── users/          # User management routes
│   │   ├── documents/      # Document processing routes
│   │   ├── chat/           # Chat and RAG routes
│   │   ├── vector/         # Vector database services
│   │   ├── core/           # Configuration and security
│   │   ├── db/             # Database models and connection
│   │   └── schemas/        # Pydantic schemas
│   ├── openAI/             # OpenAI implementation guides
│   ├── requirements.txt    # Python dependencies
│   ├── .env               # Environment variables
│   └── *.py               # Utility scripts
└── frontend/               # Streamlit Frontend (Coming Soon)
    └── (To be implemented)
```

## 🚀 Features

### Backend (FastAPI)
- ✅ **User Authentication** (JWT-based)
- ✅ **User Management** (CRUD operations)
- ✅ **Document Processing** (PDF, TXT, DOCX)
- ✅ **RAG Pipeline** (OpenAI + Pinecone)
- ✅ **Chat Interface** (RAG-powered responses)
- ✅ **Conversation History** (MongoDB storage)
- ✅ **Vector Search** (Pinecone integration)

### Frontend (Streamlit) - Coming Soon
- 🔄 **Chat Interface** (Real-time chat)
- 🔄 **File Upload** (Document processing)
- 🔄 **User Authentication** (Login/Register)
- 🔄 **Conversation History** (Past chats)

## 🛠️ Tech Stack

- **Backend**: FastAPI, MongoDB, Pinecone, OpenAI
- **Frontend**: Streamlit (planned)
- **Authentication**: JWT tokens
- **Vector DB**: Pinecone (1536 dimensions)
- **LLM**: OpenAI GPT-4o-mini
- **Embeddings**: OpenAI text-embedding-3-small

## 📋 Quick Start

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
cp env_template.txt .env
# Edit .env with your API keys
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup (Coming Soon)
```bash
cd frontend
# Streamlit app will be here
```

## 🔧 Utility Scripts

### Data Management
- `check_mongodb_status.py` - Check MongoDB status
- `check_pinecone_status.py` - Check Pinecone status
- `clear_mongodb_data.py` - Clear all MongoDB data
- `clear_pinecone_index.py` - Clear all Pinecone data
- `clear_all_data.py` - Clear both databases
- `clear_user_mongodb_data.py` - Clear specific user data
- `clear_user_data.py` - Clear specific user Pinecone data

## 📊 API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login

### Users
- `GET /users/me` - Get current user
- `GET /users/` - List all users (admin)
- `POST /users/` - Create user (admin)

### Documents
- `POST /documents/upload` - Upload document
- `GET /documents/` - List user documents
- `GET /documents/{id}` - Get document details
- `DELETE /documents/{id}` - Delete document

### Chat
- `POST /chat/query` - RAG-powered chat
- `GET /chat/history` - Get conversation history
- `GET /chat/conversation/{id}` - Get specific conversation
- `POST /chat/test` - Test OpenAI without RAG

## 🔑 Environment Variables

```bash
# MongoDB
MONGODB_URL=your_mongodb_url
DATABASE_NAME=rag_chat_app

# OpenAI
OPENAI_API_KEY=your_openai_api_key
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_LLM_MODEL=gpt-4o-mini

# Pinecone
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_PROJECT_NAME=rag-chat-app
PINECONE_INDEX_NAME=rag-chat-embeddings

# Authentication
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 🎯 Current Status

- ✅ **Backend Complete** - All APIs working
- ✅ **RAG Pipeline** - OpenAI + Pinecone integration
- ✅ **Database Models** - MongoDB with Beanie ODM
- ✅ **Authentication** - JWT-based security
- ✅ **Document Processing** - Multi-format support
- 🔄 **Frontend** - Streamlit interface (next phase)

## 📝 Next Steps

1. **Frontend Development** - Streamlit chat interface
2. **Testing** - End-to-end testing
3. **Deployment** - Production deployment
4. **Optimization** - Performance improvements

---

**Project Status**: Backend Complete ✅ | Frontend In Progress 🔄
