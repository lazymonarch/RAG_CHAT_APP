# RAG Chat Application - Frontend

Streamlit-based frontend for the RAG Chat Application.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd frontend
pip install -r requirements.txt
```

### 2. Start the Backend
Make sure the FastAPI backend is running:
```bash
cd ../backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Start the Frontend
```bash
streamlit run app.py
```

The application will be available at: http://localhost:8501

## 📁 Project Structure

```
frontend/
├── app.py                 # Main Streamlit application
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── components/           # UI components
│   ├── auth.py          # Authentication components
│   ├── chat.py          # Chat interface components
│   └── documents.py     # Document management components
├── utils/               # Utility functions
│   └── api_client.py    # API client for backend communication
└── assets/              # Static assets (images, etc.)
```

## 🎯 Features

### Authentication
- ✅ User registration and login
- ✅ JWT token management
- ✅ Session persistence
- ✅ User information display

### Document Management
- ✅ File upload (PDF, TXT, DOCX, DOC)
- ✅ Document validation
- ✅ Document listing and management
- ✅ Document statistics
- ✅ File deletion

### Chat Interface
- ✅ Real-time chat with RAG
- ✅ Message history
- ✅ Token usage tracking
- ✅ Conversation management
- ✅ Test chat (without RAG)

### User Experience
- ✅ Responsive design
- ✅ Sidebar navigation
- ✅ Tabbed interface
- ✅ Real-time updates
- ✅ Error handling

## 🔧 Configuration

Edit `config.py` to customize:

```python
# Backend API
BACKEND_URL = "http://localhost:8000"

# Streamlit settings
STREAMLIT_SERVER_PORT = 8501
APP_TITLE = "RAG Chat Application"

# File upload limits
MAX_FILE_SIZE_MB = 10
ALLOWED_FILE_TYPES = ["pdf", "txt", "docx", "doc"]
```

## 📱 Usage

### 1. Authentication
- Register a new account or login with existing credentials
- User information is displayed in the sidebar

### 2. Upload Documents
- Go to the "Documents" tab
- Click "Upload" and select your files
- Documents are automatically processed and chunked

### 3. Start Chatting
- Go to the "Chat" tab
- Type your questions about the uploaded documents
- Get AI-powered answers based on document content

### 4. View History
- Access chat history from the sidebar
- Switch between different conversations
- View token usage statistics

## 🛠️ Development

### Adding New Components
1. Create new component files in `components/`
2. Import and use in `app.py`
3. Follow the existing pattern for consistency

### API Integration
- All backend communication goes through `utils/api_client.py`
- Add new endpoints in the `APIClient` class
- Handle errors gracefully with try-catch blocks

### Styling
- Custom CSS is defined in `app.py`
- Use Streamlit's built-in components for consistency
- Follow the existing color scheme and layout

## 🐛 Troubleshooting

### Common Issues

1. **Backend Connection Error**
   - Ensure the FastAPI backend is running on port 8000
   - Check the `BACKEND_URL` in `config.py`

2. **File Upload Issues**
   - Check file size limits in `config.py`
   - Ensure file type is supported
   - Verify backend is processing files correctly

3. **Authentication Problems**
   - Clear browser cache and cookies
   - Check if JWT token is valid
   - Verify backend authentication endpoints

4. **Chat Not Working**
   - Ensure documents are uploaded and processed
   - Check if Pinecone index has vectors
   - Verify OpenAI API key is valid

### Debug Mode
Run with debug information:
```bash
streamlit run app.py --logger.level=debug
```

## 📊 Performance

### Optimization Tips
- Use `st.cache` for expensive operations
- Implement pagination for large document lists
- Use `st.empty()` for dynamic content updates
- Minimize API calls with session state

### Monitoring
- Check token usage in chat interface
- Monitor file upload success rates
- Track user engagement metrics

## 🔒 Security

### Best Practices
- JWT tokens are stored in session state
- File validation on both frontend and backend
- Input sanitization for all user inputs
- Secure API communication over HTTPS

### Environment Variables
- Never commit API keys to version control
- Use environment variables for sensitive data
- Implement proper error handling

## 📈 Future Enhancements

- [ ] Real-time notifications
- [ ] File preview functionality
- [ ] Advanced search filters
- [ ] Export chat conversations
- [ ] User preferences
- [ ] Dark mode support
- [ ] Mobile responsiveness improvements
- [ ] Advanced analytics dashboard

---

**Status**: ✅ Complete and Ready for Use
