"""
RAG Chat Application - Streamlit Frontend
"""
import streamlit as st
from config import APP_TITLE, APP_ICON, APP_LAYOUT, APP_SIDEBAR_STATE
from components.auth import (
    login_form, register_form, logout_button, 
    is_authenticated, show_register
)
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
        color: #000000;
    }
    .assistant-message {
        background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
        border-left-color: #9c27b0;
        margin-right: 20%;
        color: #000000;
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
    
    # Main header removed for cleaner UI
    
    # Sidebar
    with st.sidebar:
        # Authentication section
        if not is_authenticated():
            st.markdown("""
            <div style="text-align: center; padding: 1rem 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        border-radius: 10px; margin-bottom: 1rem; color: white;">
                <h2 style="color: white; margin: 0; font-size: 1.5rem;">🤖 RAG Chat App</h2>
                <p style="color: #f0f0f0; margin: 0.5rem 0 0 0; font-size: 0.9rem;">Get Started</p>
            </div>
            """, unsafe_allow_html=True)
            if st.session_state.get("show_register", False):
                register_form()
            else:
                login_form()
        # User info removed - using greeting in sidebar instead
    
    # Main content
    if not is_authenticated():
        # Show landing page for unauthenticated users
        show_landing_page()
    else:
        # Show main application for authenticated users
        show_main_app()


def show_landing_page():
    """Show landing page for unauthenticated users."""
    
    # Hero Section
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                border-radius: 15px; margin-bottom: 2rem; color: white;">
        <h1 style="color: white; font-size: 3rem; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">🤖 RAG Chat App</h1>
        <p style="color: #f0f0f0; font-size: 1.3rem; margin: 1rem 0; font-weight: 300;">Intelligent Document Chat with AI</p>
        <p style="color: #e0e0e0; font-size: 1.1rem; margin: 0;">Upload documents • Ask questions • Get AI-powered answers</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Features Grid
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); padding: 1.5rem; 
                    border-radius: 12px; border-left: 4px solid #28a745; margin-bottom: 1rem;">
            <h3 style="color: #28a745; margin: 0 0 1rem 0;">📄 Smart Document Processing</h3>
            <ul style="margin: 0; padding-left: 1.2rem; color: #333;">
                <li>PDF, TXT, DOCX support</li>
                <li>Intelligent text chunking</li>
                <li>Vector embeddings</li>
                <li>Semantic search ready</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); padding: 1.5rem; 
                    border-radius: 12px; border-left: 4px solid #007bff; margin-bottom: 1rem;">
            <h3 style="color: #007bff; margin: 0 0 1rem 0;">💬 AI-Powered Chat</h3>
            <ul style="margin: 0; padding-left: 1.2rem; color: #333;">
                <li>RAG technology</li>
                <li>Context-aware responses</li>
                <li>Document-specific chat</li>
                <li>Conversation history</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); padding: 1.5rem; 
                    border-radius: 12px; border-left: 4px solid #6f42c1; margin-bottom: 1rem;">
            <h3 style="color: #6f42c1; margin: 0 0 1rem 0;">🔒 Secure & Modern</h3>
            <ul style="margin: 0; padding-left: 1.2rem; color: #333;">
                <li>JWT authentication</li>
                <li>User profiles</li>
                <li>Data privacy</li>
                <li>Real-time updates</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # How It Works Section
    st.markdown("""
    <div style="background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%); padding: 2rem; 
                border-radius: 15px; margin: 2rem 0; border-left: 5px solid #ffc107;">
        <h2 style="color: #856404; margin: 0 0 1.5rem 0; text-align: center;">🚀 How It Works</h2>
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
            <div style="text-align: center; flex: 1; min-width: 150px; margin: 0.5rem;">
                <div style="background: white; border-radius: 50%; width: 60px; height: 60px; display: flex; 
                            align-items: center; justify-content: center; margin: 0 auto 1rem; font-size: 1.5rem;">1️⃣</div>
                <h4 style="color: #856404; margin: 0;">Upload</h4>
                <p style="color: #6c5ce7; margin: 0.5rem 0 0; font-size: 0.9rem;">Upload your documents</p>
            </div>
            <div style="text-align: center; flex: 1; min-width: 150px; margin: 0.5rem;">
                <div style="background: white; border-radius: 50%; width: 60px; height: 60px; display: flex; 
                            align-items: center; justify-content: center; margin: 0 auto 1rem; font-size: 1.5rem;">2️⃣</div>
                <h4 style="color: #856404; margin: 0;">Process</h4>
                <p style="color: #6c5ce7; margin: 0.5rem 0 0; font-size: 0.9rem;">AI processes & indexes</p>
            </div>
            <div style="text-align: center; flex: 1; min-width: 150px; margin: 0.5rem;">
                <div style="background: white; border-radius: 50%; width: 60px; height: 60px; display: flex; 
                            align-items: center; justify-content: center; margin: 0 auto 1rem; font-size: 1.5rem;">3️⃣</div>
                <h4 style="color: #856404; margin: 0;">Chat</h4>
                <p style="color: #6c5ce7; margin: 0.5rem 0 0; font-size: 0.9rem;">Ask questions & get answers</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Call to Action
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                border-radius: 15px; margin: 2rem 0; color: white;">
        <h2 style="color: white; margin: 0 0 1rem 0;">Ready to Get Started?</h2>
        <p style="color: #f0f0f0; font-size: 1.1rem; margin: 0 0 1.5rem 0;">Join thousands of users who are already using AI to chat with their documents!</p>
        <div style="display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap;">
            <div style="background: rgba(255,255,255,0.2); padding: 1rem; border-radius: 10px; min-width: 200px;">
                <h4 style="color: white; margin: 0 0 0.5rem 0;">✨ Free to Use</h4>
                <p style="color: #e0e0e0; margin: 0; font-size: 0.9rem;">No hidden costs, no subscriptions</p>
            </div>
            <div style="background: rgba(255,255,255,0.2); padding: 1rem; border-radius: 10px; min-width: 200px;">
                <h4 style="color: white; margin: 0 0 0.5rem 0;">🔒 Secure & Private</h4>
                <p style="color: #e0e0e0; margin: 0; font-size: 0.9rem;">Your data stays private and secure</p>
            </div>
        </div>
        <p style="color: #f0f0f0; font-size: 1rem; margin: 1.5rem 0 0 0; font-weight: 500;">
            👈 Use the sidebar to <strong>Login</strong> or <strong>Register</strong> and start your AI journey!
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Technology Stack
    st.markdown("""
    <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 12px; margin: 1rem 0; border: 1px solid #dee2e6;">
        <h3 style="color: #495057; margin: 0 0 1rem 0; text-align: center;">🛠️ Powered by Modern Technology</h3>
        <div style="display: flex; justify-content: center; align-items: center; flex-wrap: wrap; gap: 1rem;">
            <span style="background: #e3f2fd; color: #1976d2; padding: 0.5rem 1rem; border-radius: 20px; font-weight: 500;">FastAPI</span>
            <span style="background: #f3e5f5; color: #7b1fa2; padding: 0.5rem 1rem; border-radius: 20px; font-weight: 500;">Streamlit</span>
            <span style="background: #e8f5e8; color: #388e3c; padding: 0.5rem 1rem; border-radius: 20px; font-weight: 500;">MongoDB</span>
            <span style="background: #fff3e0; color: #f57c00; padding: 0.5rem 1rem; border-radius: 20px; font-weight: 500;">Pinecone</span>
            <span style="background: #fce4ec; color: #c2185b; padding: 0.5rem 1rem; border-radius: 20px; font-weight: 500;">OpenAI</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def show_main_app():
    """Show main application for authenticated users."""
    # Initialize session state for current page
    if "current_page" not in st.session_state:
        st.session_state.current_page = "universal_chat"
    
    # Left Sidebar with 3 main sections
    with st.sidebar:
        # User Greeting - at the top
        try:
            from utils.api_client import api_client
            user_data = api_client.get_user_profile()
            user_name = user_data.get('name', 'User')
            st.markdown(f"### 👋 Hi {user_name}")
        except:
            st.markdown("### 👋 Hi User")
        
        st.markdown("---")
        
        # Back button - smart navigation
        if st.button("← Back", use_container_width=True, type="secondary"):
            current_page = st.session_state.get("current_page", "universal_chat")
            
            # Smart back navigation based on current page
            if current_page == "document_chat":
                st.session_state.current_page = "universal_chat"
            elif current_page == "documents":
                st.session_state.current_page = "universal_chat"
            elif current_page == "chat_history":
                st.session_state.current_page = "universal_chat"
            elif current_page == "profile":
                st.session_state.current_page = "universal_chat"
            else:
                st.session_state.current_page = "universal_chat"
            
            st.rerun()
        
        st.markdown("---")
        
        # Section 1: Universal Chat
        if st.button("💬 Universal Chat", use_container_width=True, type="primary"):
            st.session_state.current_page = "universal_chat"
            st.rerun()
        
        # Section 2: Document Chat
        if st.button("📄 Document Chat", use_container_width=True):
            st.session_state.current_page = "document_chat"
            st.rerun()
        
        # Section 3: Documents
        if st.button("📁 Documents", use_container_width=True):
            st.session_state.current_page = "documents"
            st.rerun()
        
        # Section 4: Chats (renamed from Chat History)
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
    elif st.session_state.current_page == "document_chat":
        show_document_chat()
    elif st.session_state.current_page == "documents":
        show_documents_page()
    elif st.session_state.current_page == "chat_history":
        show_chat_history_page()
    elif st.session_state.current_page == "profile":
        show_profile_page()


def show_documents_page():
    """Show documents management page."""
    
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
    
    # Chat Interface - Always show input field for Universal Chat
    if "current_conversation_id" not in st.session_state or st.session_state.current_conversation_id is None:
        # Auto-start a conversation for Universal Chat
        start_new_conversation()
    
    # Show chat interface
    show_chat_interface()


def show_document_chat():
    """Show document chat interface."""
    
    # Chat Mode Indicator
    st.info("📄 **Document Mode**: Choose specific documents to chat with")
    
    # Document Selection
    try:
        from utils.api_client import api_client
        documents = api_client.get_selectable_documents()
        
        if not documents:
            st.warning("📄 No documents available. Upload documents first!")
            return
        
        st.subheader("📋 Select Documents")
        
        # Document selection checkboxes
        selected_docs = []
        col1, col2 = st.columns(2)
        
        for i, doc in enumerate(documents):
            with col1 if i % 2 == 0 else col2:
                if st.checkbox(
                    f"📄 {doc['original_filename']}",
                    key=f"doc_{doc['id']}",
                    help=f"Type: {doc['file_type']}, Size: {doc['file_size']} bytes"
                ):
                    selected_docs.append(doc['id'])
        
        # Start chat button
        if selected_docs:
            st.success(f"✅ Selected {len(selected_docs)} document(s)")
            
            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button("🚀 Start Document Chat", type="primary"):
                    start_document_conversation(selected_docs)
        else:
            st.info("👆 Select one or more documents to start chatting")
    
    except Exception as e:
        st.error(f"Error loading documents: {str(e)}")
    
    # Show current document chat if active (only after document selection)
    if ("current_conversation_id" in st.session_state and 
        st.session_state.current_conversation_id and 
        st.session_state.get("current_page") == "document_chat" and
        st.session_state.get("conversation_type") == "document"):
        st.markdown("---")
        show_chat_interface()


def show_chat_interface():
    """Show the actual chat interface."""
    # Get conversation details
    conversation_id = st.session_state.current_conversation_id
    
    # Load conversation messages if not already loaded
    if "chat_messages" not in st.session_state or not st.session_state.chat_messages:
        load_conversation_messages(conversation_id)
    
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
    
    # Chat input - use session state to manage input clearing
    input_key = f"chat_input_{conversation_id}"
    
    # Initialize input state if not exists
    if f"input_cleared_{conversation_id}" not in st.session_state:
        st.session_state[f"input_cleared_{conversation_id}"] = False
    
    # Clear input if needed
    if st.session_state[f"input_cleared_{conversation_id}"]:
        user_input = st.text_input("Type your message:", key=input_key, value="")
        st.session_state[f"input_cleared_{conversation_id}"] = False
    else:
        user_input = st.text_input("Type your message:", key=input_key)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("Send", type="primary"):
            if user_input:
                send_message(user_input)
                # Mark input for clearing on next render
                st.session_state[f"input_cleared_{conversation_id}"] = True
                st.rerun()
    
    with col2:
        if st.button("End Chat"):
            end_current_chat()
            st.rerun()
    
    with col3:
        if st.button("📧 Email Chat"):
            email_chat_summary(conversation_id)


def show_chat_history_page():
    """Show chat history page."""
    
    # Chat history
    try:
        from utils.api_client import api_client
        
        # Get chat history
        try:
            chat_history = api_client.get_chat_history()
            
            if not chat_history:
                st.info("No chat history available. Start a conversation in the Chat section!")
                return
            
            # Filter out conversations with 0 messages
            conversations_with_messages = [
                conv for conv in chat_history 
                if conv.get('message_count', 0) > 0
            ]
            
            if not conversations_with_messages:
                st.info("No conversations with messages found. Start chatting to see your history here!")
                return
            
            # Display conversations
            for i, conversation in enumerate(conversations_with_messages):
                # Create simple title
                title = conversation.get('title', 'Untitled Conversation')
                display_title = f"💬 {title}"
                
                # Simple conversation card
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.write(f"**{display_title}**")
                    st.caption(f"Created: {conversation.get('created_at', 'Unknown')[:10]} • Messages: {conversation.get('message_count', 0)}")
                
                with col2:
                    if st.button(f"📖 View", key=f"view_{conversation['id']}"):
                        view_conversation(conversation['id'])
                
                with col3:
                    if st.button(f"🗑️ Delete", key=f"delete_{conversation['id']}"):
                        delete_conversation(conversation['id'])
                
                st.markdown("---")
        
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
        st.session_state.conversation_type = conversation.get("chat_type", "universal")
        st.session_state.chat_messages = []
        
        # Load messages
        messages = conversation.get("messages", [])
        for msg in messages:
            st.session_state.chat_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Switch to appropriate chat page based on conversation type
        if conversation.get("chat_type") == "document":
            st.session_state.current_page = "document_chat"
        else:
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
        
        # Action Buttons
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("← Back to Chat", type="primary"):
                st.session_state.current_page = "universal_chat"
                st.rerun()
        
        with col2:
            if st.button("🗑️ Delete Profile", type="secondary"):
                st.session_state.show_delete_confirmation = True
                st.rerun()
        
        # Delete Profile Confirmation Dialog
        if st.session_state.get("show_delete_confirmation", False):
            st.markdown("---")
            st.error("⚠️ **DANGER ZONE**")
            st.warning("""
            **This action cannot be undone!**
            
            Deleting your profile will permanently remove:
            - Your account and personal information
            - All your chat conversations and messages
            - All your uploaded documents
            - All your data from our systems
            
            Are you absolutely sure you want to delete your profile?
            """)
            
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                if st.button("✅ Yes, Delete Everything", type="primary"):
                    delete_user_profile()
            
            with col2:
                if st.button("❌ Cancel", type="secondary"):
                    st.session_state.show_delete_confirmation = False
                    st.rerun()
            
            with col3:
                if st.button("🔒 Keep Profile", type="secondary"):
                    st.session_state.show_delete_confirmation = False
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
        st.session_state.conversation_type = "universal"  # Set conversation type
        st.session_state.chat_messages = []
        st.success("New conversation started!")
    except Exception as e:
        st.error(f"Failed to start conversation: {str(e)}")


def start_document_conversation(document_ids: list):
    """Start a new document-scoped conversation."""
    try:
        from utils.api_client import api_client
        result = api_client.start_document_conversation(document_ids)
        st.session_state.current_conversation_id = result["conversation_id"]
        st.session_state.conversation_type = "document"  # Set conversation type
        st.session_state.chat_messages = []
        st.success(f"Document chat started with {len(document_ids)} document(s)!")
        st.rerun()
    except Exception as e:
        st.error(f"Failed to start document conversation: {str(e)}")


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
        # If conversation doesn't exist or has no messages, initialize empty
        if "not found" in str(e).lower() or "404" in str(e):
            st.session_state.chat_messages = []
        else:
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
        
    except Exception as e:
        st.error(f"Failed to send message: {str(e)}")
        # Remove the user message if sending failed
        if st.session_state.chat_messages and st.session_state.chat_messages[-1]["role"] == "user":
            st.session_state.chat_messages.pop()


def end_current_chat():
    """End the current chat session."""
    st.session_state.current_conversation_id = None
    st.session_state.conversation_type = None
    st.session_state.chat_messages = []
    st.success("Chat session ended!")


def email_chat_summary(conversation_id: str):
    """Send chat summary via email."""
    try:
        from utils.api_client import api_client
        result = api_client.email_chat_summary(conversation_id)
        st.success(result.get("message", "Chat summary sent to your email!"))
    except Exception as e:
        st.error(f"Failed to send email: {str(e)}")


def delete_user_profile():
    """Delete user profile and all associated data."""
    try:
        from utils.api_client import api_client
        result = api_client.delete_profile()
        
        if result.get("message"):
            # Clear all session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            
            # Show success message
            st.success("✅ Profile deleted successfully!")
            st.info("All your data has been permanently removed from our systems.")
            
            # Redirect to login after a short delay
            st.markdown("Redirecting to login page...")
            st.rerun()
        else:
            st.error(f"Failed to delete profile: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        st.error(f"Failed to delete profile: {str(e)}")
        st.session_state.show_delete_confirmation = False


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
    if "conversation_type" in st.session_state:
        del st.session_state.conversation_type
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
