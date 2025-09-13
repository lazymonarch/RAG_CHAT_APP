"""
RAG Chat Application - Streamlit Frontend
"""
import streamlit as st
from streamlit_option_menu import option_menu
from config import APP_TITLE, APP_ICON, APP_LAYOUT, APP_SIDEBAR_STATE
from components.auth import (
    login_form, register_form, logout_button, user_info, 
    is_authenticated, show_register
)
from components.chat import chat_interface, chat_history_sidebar, test_chat
from components.documents import document_upload, document_list, document_stats


def main():
    """Main application function."""
    # Page configuration
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=APP_ICON,
        layout=APP_LAYOUT,
        initial_sidebar_state=APP_SIDEBAR_STATE
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        border-bottom: 2px solid #e0e0e0;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
    }
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
    }
    .main-header p {
        color: #f0f0f0;
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
    }
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 15px;
        border-left: 4px solid #1f77b4;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.2s ease;
    }
    .chat-message:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    .user-message {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border-left-color: #2196f3;
        margin-left: 20%;
    }
    .assistant-message {
        background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
        border-left-color: #9c27b0;
        margin-right: 20%;
    }
    .metric-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #dee2e6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.2s ease;
        color: #000000;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    .metric-card h4 {
        color: #000000;
        margin: 0 0 0.5rem 0;
    }
    .metric-card h2 {
        color: #000000;
        margin: 0.5rem 0;
    }
    .metric-card p {
        color: #000000;
        margin: 0;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 2px solid #e0e0e0;
        padding: 0.5rem;
        transition: border-color 0.3s ease;
    }
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    .conversation-card {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    .conversation-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        border-color: #667eea;
    }
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 0.5rem;
    }
    .status-online {
        background-color: #4caf50;
    }
    .status-offline {
        background-color: #f44336;
    }
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid #f3f3f3;
        border-top: 3px solid #667eea;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main header
    st.markdown(f"""
    <div class="main-header">
        <h1>{APP_ICON} {APP_TITLE}</h1>
        <p>Upload documents and chat with AI using RAG technology</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        # Authentication section
        if not is_authenticated():
            st.title("🎛️ Control Panel")
            st.markdown("---")
            if st.session_state.get("show_register", False):
                register_form()
            else:
                login_form()
        else:
            # User info only
            user_info()
    
    # Main content
    if not is_authenticated():
        # Show landing page for unauthenticated users
        show_landing_page()
    else:
        # Show main application for authenticated users
        show_main_app()


def show_landing_page():
    """Show landing page for unauthenticated users."""
    st.markdown("""
    ## Welcome to RAG Chat Application! 🤖
    
    This application allows you to:
    
    ### 📄 Upload Documents
    - Upload PDF, TXT, DOCX, or DOC files
    - Documents are automatically processed and chunked
    - Vector embeddings are created for semantic search
    
    ### 💬 Chat with AI
    - Ask questions about your uploaded documents
    - Get answers based on document content (RAG)
    - View conversation history
    
    ### 🔍 Features
    - **RAG Technology**: Retrieval-Augmented Generation
    - **Vector Search**: Semantic similarity search
    - **Multiple Formats**: Support for various document types
    - **User Management**: Secure authentication
    - **Real-time Chat**: Interactive conversation interface
    
    ### 🚀 Getting Started
    1. **Register** or **Login** using the sidebar
    2. **Upload** your documents
    3. **Start chatting** with the AI about your content!
    
    ---
    
    **Ready to get started?** Use the sidebar to login or register!
    """)


def show_main_app():
    """Show main application for authenticated users."""
    # Initialize session state for current page
    if "current_page" not in st.session_state:
        st.session_state.current_page = "universal_chat"
    
    # Left Sidebar with 3 main sections
    with st.sidebar:
        # Back button
        if st.button("← Back", use_container_width=True, type="secondary"):
            if st.session_state.current_page != "universal_chat":
                st.session_state.current_page = "universal_chat"
                st.rerun()
        
        st.markdown("---")
        
        # Section 1: Universal Chat
        if st.button("💬 Universal Chat", use_container_width=True, type="primary"):
            st.session_state.current_page = "universal_chat"
            st.rerun()
        
        # Section 2: Documents
        if st.button("📄 Documents", use_container_width=True):
            st.session_state.current_page = "documents"
            st.rerun()
        
        # Section 3: Chats (renamed from Chat History)
        if st.button("💬 Chats", use_container_width=True):
            st.session_state.current_page = "chat_history"
            st.rerun()
        
        st.markdown("---")
        
        # Profile and Logout Section
        if st.button("👤 Profile", use_container_width=True, type="secondary"):
            st.session_state.current_page = "profile"
            st.rerun()
        
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            # Clear all session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.success("Logged out successfully!")
            st.rerun()
    
    # Top Right Menu (simplified - no logout needed)
    st.markdown("---")
    
    # Main Content Area
    if st.session_state.current_page == "universal_chat":
        show_universal_chat()
    elif st.session_state.current_page == "documents":
        show_documents_page()
    elif st.session_state.current_page == "chat_history":
        show_chat_history_page()
    elif st.session_state.current_page == "profile":
        show_profile_page()


def show_documents_page():
    """Show documents management page."""
    st.title("📄 Document Management")
    
    # Upload section
    st.subheader("📤 Upload New Document")
    document_upload()
    
    st.markdown("---")
    
    # Documents list and stats in one view
    col1, col2 = st.columns([2, 1])
    
    with col1:
        document_list()
    
    with col2:
        document_stats()


def show_universal_chat():
    """Show universal chat interface."""
    st.title("💬 Universal Chat")
    
    # Chat Mode Indicator
    st.info("🌐 **Universal Mode**: Searching across all your uploaded documents")
    
    # Document Status
    try:
        from utils.api_client import api_client
        documents = api_client.get_documents()
        doc_count = len(documents)
        if doc_count > 0:
            st.success(f"📄 Active Documents: {doc_count}")
        else:
            st.warning("📄 No documents uploaded yet. Upload documents to start chatting!")
    except Exception as e:
        st.warning("📄 Unable to load document count. Please check your connection.")
    
    # Chat Interface
    if "current_conversation_id" not in st.session_state or st.session_state.current_conversation_id is None:
        if st.button("🚀 Start New Chat", type="primary"):
            start_new_conversation()
    else:
        show_chat_interface()


def show_chat_interface():
    """Show the actual chat interface."""
    st.subheader("💬 Chat Interface")
    
    # Get conversation details
    conversation_id = st.session_state.current_conversation_id
    
    # Load conversation messages if not already loaded
    if "chat_messages" not in st.session_state or not st.session_state.chat_messages:
        load_conversation_messages(conversation_id)
    
    # Display conversation info
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.info(f"💬 **Active Conversation:** {conversation_id[:8]}...")
    with col2:
        st.success("🟢 Online")
    with col3:
        if st.button("📊 View Details"):
            show_conversation_details(conversation_id)
    
    # Display messages
    if st.session_state.chat_messages:
        for i, message in enumerate(st.session_state.chat_messages):
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>👤 You:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <strong>🤖 AI:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("💬 Start the conversation by typing a message below!")
        st.markdown("""
        <div style="text-align: center; padding: 2rem; color: #666;">
            <h3>🚀 Ready to Chat!</h3>
            <p>Ask me anything about your uploaded documents. I'll search through all your content to provide accurate answers.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Chat input
    user_input = st.text_input("Type your message:", key="chat_input")
    
    col1, col2, col3 = st.columns([1, 1, 3])
    
    with col1:
        if st.button("Send", type="primary"):
            if user_input:
                send_message(user_input)
                st.rerun()
    
    with col2:
        if st.button("End Chat"):
            end_current_chat()
            st.rerun()
    
    with col3:
        if st.button("🔄 Refresh Messages"):
            load_conversation_messages(conversation_id)
            st.rerun()


def show_chat_history_page():
    """Show chat history page."""
    st.title("💬 Chats")
    
    # Get user info
    try:
        from utils.api_client import api_client
        user_data = api_client.get_current_user()
        
        st.info(f"👤 **Logged in as:** {user_data.get('name', user_data.get('email', 'Unknown'))}")
        
        # Chat history
        st.markdown("---")
        st.subheader("💬 Your Conversations")
        
        # Get chat history
        try:
            chat_history = api_client.get_chat_history()
            
            if not chat_history:
                st.info("No chat history available. Start a conversation in the Chat section!")
                return
            
            # Display conversations
            for i, conversation in enumerate(chat_history):
                with st.expander(f"💬 {conversation.get('title', 'Untitled Conversation')} - {conversation.get('created_at', 'Unknown date')[:10]}"):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.write(f"**Messages:** {conversation.get('message_count', 0)}")
                        st.write(f"**Created:** {conversation.get('created_at', 'Unknown')}")
                    
                    with col2:
                        if st.button(f"📖 View", key=f"view_{conversation['id']}"):
                            view_conversation(conversation['id'])
                    
                    with col3:
                        if st.button(f"🗑️ Delete", key=f"delete_{conversation['id']}"):
                            delete_conversation(conversation['id'])
                    
                    # Show recent messages preview
                    st.write("**Recent Messages Preview:**")
                    try:
                        conv_details = api_client.get_conversation(conversation['id'])
                        messages = conv_details.get('messages', [])
                        if messages:
                            for msg in messages[-3:]:  # Show last 3 messages
                                role = "👤 You" if msg.get('role') == 'user' else "🤖 AI"
                                content = msg.get('content', '')[:100]
                                if len(msg.get('content', '')) > 100:
                                    content += "..."
                                st.write(f"{role}: {content}")
                        else:
                            st.write("No messages in this conversation.")
                    except Exception as e:
                        st.write(f"Error loading messages: {str(e)}")
        
        except Exception as e:
            st.error(f"Error loading chat history: {str(e)}")
    
    except Exception as e:
        st.error(f"Error loading user info: {str(e)}")


def view_conversation(conversation_id: str):
    """View a specific conversation."""
    try:
        from utils.api_client import api_client
        conversation = api_client.get_conversation(conversation_id)
        
        st.session_state.current_conversation_id = conversation_id
        st.session_state.chat_messages = []
        
        # Load messages
        messages = conversation.get("messages", [])
        for msg in messages:
            st.session_state.chat_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Switch to chat page
        st.session_state.current_page = "universal_chat"
        st.rerun()
        
    except Exception as e:
        st.error(f"Failed to load conversation: {str(e)}")


def delete_conversation(conversation_id: str):
    """Delete a conversation."""
    try:
        from utils.api_client import api_client
        api_client.delete_conversation(conversation_id)
        st.success("Conversation deleted successfully!")
        st.rerun()
        
    except Exception as e:
        st.error(f"Failed to delete conversation: {str(e)}")


def show_conversation_details(conversation_id: str):
    """Show detailed conversation information."""
    try:
        from utils.api_client import api_client
        conversation = api_client.get_conversation(conversation_id)
        
        st.subheader("📊 Conversation Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**ID:** {conversation_id}")
            st.write(f"**Title:** {conversation.get('title', 'Untitled')}")
            st.write(f"**Created:** {conversation.get('created_at', 'Unknown')}")
        
        with col2:
            st.write(f"**Messages:** {len(conversation.get('messages', []))}")
            st.write(f"**Last Updated:** {conversation.get('updated_at', 'Unknown')}")
            st.write(f"**Status:** Active")
        
        # Show sources if available
        if 'sources' in conversation and conversation['sources']:
            st.subheader("📚 Sources Used")
            for source in conversation['sources']:
                st.write(f"• {source.get('filename', 'Unknown')} (Score: {source.get('score', 0):.2f})")
        
    except Exception as e:
        st.error(f"Failed to load conversation details: {str(e)}")


def show_profile_page():
    """Show user profile page with statistics."""
    st.title("👤 User Profile")
    
    try:
        from utils.api_client import api_client
        user_data = api_client.get_user_profile()
        
        # User Information Section
        st.subheader("📋 Personal Information")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h4>👤 Name</h4>
                <p>{user_data.get('name', 'Not set')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-card">
                <h4>📧 Email</h4>
                <p>{user_data.get('email', 'Unknown')}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h4>📅 Member Since</h4>
                <p>{user_data.get('created_at', 'Unknown')[:10]}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-card">
                <h4>🔐 Account Status</h4>
                <p>✅ Active</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Statistics Section
        st.subheader("📊 Usage Statistics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h4>📄 Documents</h4>
                <h2>{user_data.get('document_count', 0)}</h2>
                <p>Uploaded</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h4>💬 Chats</h4>
                <h2>{user_data.get('chat_count', 0)}</h2>
                <p>Created</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h4>💭 Messages</h4>
                <h2>{user_data.get('message_count', 0)}</h2>
                <p>Total</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Storage Section
        st.subheader("💾 Storage Usage")
        storage_used = user_data.get('storage_used', 0) / (1024*1024)  # Convert to MB
        storage_limit = user_data.get('storage_limit', 0) / (1024*1024)  # Convert to MB
        storage_percent = user_data.get('storage_percentage', 0)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.progress(storage_percent / 100)
            st.caption(f"Used: {storage_used:.2f} MB / {storage_limit:.2f} MB")
        
        with col2:
            st.metric("Storage Used", f"{storage_used:.2f} MB", f"{storage_percent:.1f}%")
        
        # Back Button
        st.markdown("---")
        if st.button("← Back to Chat", type="primary"):
            st.session_state.current_page = "universal_chat"
            st.rerun()
    
    except Exception as e:
        st.error(f"Error loading profile: {str(e)}")
        if st.button("← Back to Chat", type="primary"):
            st.session_state.current_page = "universal_chat"
            st.rerun()


def start_new_conversation():
    """Start a new conversation."""
    try:
        from utils.api_client import api_client
        result = api_client.start_conversation()
        st.session_state.current_conversation_id = result["conversation_id"]
        st.session_state.chat_messages = []
        st.success("New conversation started!")
    except Exception as e:
        st.error(f"Failed to start conversation: {str(e)}")


def load_conversation_messages(conversation_id: str):
    """Load messages for a conversation."""
    try:
        from utils.api_client import api_client
        conversation = api_client.get_conversation(conversation_id)
        
        # Extract messages from conversation
        messages = conversation.get("messages", [])
        st.session_state.chat_messages = []
        
        for msg in messages:
            st.session_state.chat_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
            
    except Exception as e:
        st.error(f"Failed to load conversation messages: {str(e)}")
        st.session_state.chat_messages = []


def send_message(message: str):
    """Send a message to the current conversation."""
    try:
        from utils.api_client import api_client
        conversation_id = st.session_state.current_conversation_id
        
        # Add user message to session state
        st.session_state.chat_messages.append({
            "role": "user",
            "content": message
        })
        
        # Show loading state
        with st.spinner("🤖 AI is thinking..."):
            # Send to backend
            response = api_client.send_message(conversation_id, message)
            
            # Add assistant response to session state
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": response["message"]
            })
        
        # Clear the input
        st.session_state.chat_input = ""
        
    except Exception as e:
        st.error(f"Failed to send message: {str(e)}")
        # Remove the user message if sending failed
        if st.session_state.chat_messages and st.session_state.chat_messages[-1]["role"] == "user":
            st.session_state.chat_messages.pop()


def end_current_chat():
    """End the current chat session."""
    st.session_state.current_conversation_id = None
    st.session_state.chat_messages = []
    st.success("Chat session ended!")


def logout_user():
    """Logout the current user."""
    # Clear all session state variables
    if "access_token" in st.session_state:
        del st.session_state.access_token
    if "user_email" in st.session_state:
        del st.session_state.user_email
    if "user_id" in st.session_state:
        del st.session_state.user_id
    if "current_conversation_id" in st.session_state:
        del st.session_state.current_conversation_id
    if "chat_messages" in st.session_state:
        del st.session_state.chat_messages
    if "user_documents" in st.session_state:
        del st.session_state.user_documents
    if "show_profile" in st.session_state:
        del st.session_state.show_profile
    if "current_page" in st.session_state:
        del st.session_state.current_page
    if "show_register" in st.session_state:
        del st.session_state.show_register
    
    st.success("Logged out successfully!")
    st.rerun()  # Refresh the page to show login form


if __name__ == "__main__":
    main()
