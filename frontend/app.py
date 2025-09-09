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
    }
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left-color: #2196f3;
    }
    .assistant-message {
        background-color: #f3e5f5;
        border-left-color: #9c27b0;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
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
        st.title("🎛️ Control Panel")
        
        # Authentication section
        if not is_authenticated():
            st.markdown("---")
            if st.session_state.get("show_register", False):
                register_form()
            else:
                login_form()
        else:
            # User info
            user_info()
            st.markdown("---")
            
            # Logout button
            logout_button()
            
            # Chat history
            st.markdown("---")
            chat_history_sidebar()
    
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
    # Navigation menu - Simplified to core functionality
    selected = option_menu(
        menu_title=None,
        options=["💬 Chat", "📄 Documents", "📚 History"],
        icons=["chat", "file-text", "clock-history"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#fafafa"},
            "icon": {"color": "orange", "font-size": "25px"},
            "nav-link": {
                "font-size": "16px",
                "text-align": "center",
                "margin": "0px",
                "--hover-color": "#eee"
            },
            "nav-link-selected": {"background-color": "#02ab21"},
        }
    )
    
    # Route to appropriate page
    if selected == "💬 Chat":
        chat_interface()
    elif selected == "📄 Documents":
        show_documents_page()
    elif selected == "📚 History":
        show_chat_history_page()


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


def show_chat_history_page():
    """Show chat history page."""
    st.title("📚 Chat History")
    
    # Get user info
    try:
        from utils.api_client import api_client
        user_data = api_client.get_current_user()
        
        st.info(f"👤 **Logged in as:** {user_data.get('name', user_data.get('email', 'Unknown'))}")
        
        # Chat history
        st.markdown("---")
        st.subheader("💬 Recent Conversations")
        
        # Get chat history
        try:
            chat_history = api_client.get_chat_history()
            
            if not chat_history:
                st.info("No chat history available. Start a conversation in the Chat section!")
                return
            
            # Display conversations
            for i, conversation in enumerate(chat_history):
                with st.expander(f"💬 Conversation {i+1} - {conversation.get('created_at', 'Unknown date')[:10]}"):
                    st.write(f"**Messages:** {conversation.get('message_count', 0)}")
                    st.write(f"**Created:** {conversation.get('created_at', 'Unknown')}")
                    
                    # Show recent messages
                    if 'messages' in conversation and conversation['messages']:
                        st.write("**Recent Messages:**")
                        for msg in conversation['messages'][-3:]:  # Show last 3 messages
                            role = "👤 You" if msg.get('role') == 'user' else "🤖 AI"
                            st.write(f"{role}: {msg.get('content', '')[:100]}...")
        
        except Exception as e:
            st.error(f"Error loading chat history: {str(e)}")
    
    except Exception as e:
        st.error(f"Error loading user info: {str(e)}")


if __name__ == "__main__":
    main()
