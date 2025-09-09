"""
Chat Components
"""
import streamlit as st
from streamlit_chat import message
from utils.api_client import api_client
from components.auth import require_auth
import time


def chat_interface():
    """Main chat interface."""
    if not require_auth():
        return
    
    st.subheader("💬 RAG Chat")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "current_conversation_id" not in st.session_state:
        st.session_state.current_conversation_id = None
    
    # Chat input
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        with col1:
            user_input = st.text_input(
                "Type your message...",
                placeholder="Ask me anything about your documents!",
                label_visibility="collapsed"
            )
        with col2:
            send_button = st.form_submit_button("Send", use_container_width=True)
    
    # Send message
    if send_button and user_input:
        # Add user message to chat
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": time.time()
        })
        
        # Send to API
        try:
            with st.spinner("Thinking..."):
                response = api_client.send_message(user_input)
            
            # Add assistant response to chat
            st.session_state.messages.append({
                "role": "assistant",
                "content": response["content"],
                "timestamp": time.time(),
                "usage": response.get("usage", {})
            })
            
            # Update conversation ID if new
            if "conversation_id" in response:
                st.session_state.current_conversation_id = response["conversation_id"]
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.session_state.messages.append({
                "role": "assistant",
                "content": "Sorry, I encountered an error. Please try again.",
                "timestamp": time.time()
            })
    
    # Display chat messages
    display_chat_messages()
    
    # Chat controls
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.current_conversation_id = None
            st.rerun()
    
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    with col3:
        if st.button("📊 Show Usage", use_container_width=True):
            show_usage_stats()


def display_chat_messages():
    """Display chat messages."""
    if not st.session_state.messages:
        st.info("👋 Hello! Upload some documents and start chatting with me!")
        return
    
    # Display messages
    for i, msg in enumerate(st.session_state.messages):
        if msg["role"] == "user":
            message(
                msg["content"],
                is_user=True,
                key=f"user_{i}",
                avatar_style="adventurer"
            )
        else:
            message(
                msg["content"],
                is_user=False,
                key=f"assistant_{i}",
                avatar_style="bottts"
            )


def show_usage_stats():
    """Show token usage statistics."""
    if not st.session_state.messages:
        st.info("No messages to show usage for")
        return
    
    # Calculate total usage
    total_prompt_tokens = 0
    total_completion_tokens = 0
    total_tokens = 0
    
    for msg in st.session_state.messages:
        if msg["role"] == "assistant" and "usage" in msg:
            usage = msg["usage"]
            total_prompt_tokens += usage.get("prompt_tokens", 0)
            total_completion_tokens += usage.get("completion_tokens", 0)
            total_tokens += usage.get("total_tokens", 0)
    
    if total_tokens > 0:
        st.subheader("📊 Token Usage")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Prompt Tokens", total_prompt_tokens)
        with col2:
            st.metric("Completion Tokens", total_completion_tokens)
        with col3:
            st.metric("Total Tokens", total_tokens)
        
        # Cost estimation (approximate)
        estimated_cost = (total_prompt_tokens * 0.15 + total_completion_tokens * 0.60) / 1000000
        st.info(f"💰 Estimated Cost: ${estimated_cost:.4f}")
    else:
        st.info("No usage data available")


def chat_history_sidebar():
    """Display chat history in sidebar."""
    if not require_auth():
        return
    
    st.sidebar.subheader("📚 Chat History")
    
    try:
        # Check if chat history is cached
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = api_client.get_chat_history()
        
        history = st.session_state.chat_history
        
        if not history:
            st.sidebar.info("No chat history yet")
            return
        
        for conv in history:
            if st.sidebar.button(
                conv["title"][:50] + "..." if len(conv["title"]) > 50 else conv["title"],
                key=f"conv_{conv['id']}",
                use_container_width=True
            ):
                load_conversation(conv["id"])
    
    except Exception as e:
        st.sidebar.error(f"Error loading history: {str(e)}")


def load_conversation(conversation_id: str):
    """Load a specific conversation."""
    try:
        conversation = api_client.get_conversation(conversation_id)
        
        # Clear current messages
        st.session_state.messages = []
        
        # Load conversation messages
        for msg in conversation["messages"]:
            st.session_state.messages.append({
                "role": msg["role"],
                "content": msg["content"],
                "timestamp": msg["timestamp"]
            })
        
        st.session_state.current_conversation_id = conversation_id
        st.rerun()
        
    except Exception as e:
        st.error(f"Error loading conversation: {str(e)}")


def test_chat():
    """Test chat without RAG."""
    if not require_auth():
        return
    
    st.subheader("🧪 Test Chat (No RAG)")
    
    with st.form("test_chat_form", clear_on_submit=True):
        test_input = st.text_input(
            "Test message...",
            placeholder="Test OpenAI without document context",
            label_visibility="collapsed"
        )
        test_button = st.form_submit_button("Test", use_container_width=True)
    
    if test_button and test_input:
        try:
            with st.spinner("Testing..."):
                response = api_client.test_chat(test_input)
            
            st.success("Test successful!")
            st.write("**Response:**")
            st.write(response["response"])
            
            if "usage" in response:
                st.write("**Usage:**")
                st.json(response["usage"])
        
        except Exception as e:
            st.error(f"Test failed: {str(e)}")
