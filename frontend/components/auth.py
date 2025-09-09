"""
Authentication Components
"""
import streamlit as st
from utils.api_client import api_client


def login_form():
    """Display login form."""
    st.subheader("🔐 Login")
    
    with st.form("login_form"):
        email = st.text_input("Email", placeholder="Enter your email")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            login_button = st.form_submit_button("Login", use_container_width=True)
        with col2:
            register_button = st.form_submit_button("Switch to Register", use_container_width=True)
    
    if login_button:
        if email and password:
            try:
                response = api_client.login(email, password)
                st.session_state.access_token = response["access_token"]
                st.session_state.user_email = email
                # Get user_id from token or fetch user details
                st.session_state.user_id = None  # Will be fetched later
                st.success("Login successful!")
                st.rerun()
            except Exception as e:
                st.error(f"Login failed: {str(e)}")
        else:
            st.error("Please fill in all fields")
    
    if register_button:
        st.session_state.show_register = True
        st.rerun()


def register_form():
    """Display registration form."""
    st.subheader("📝 Register")
    
    with st.form("register_form"):
        name = st.text_input("Full Name", placeholder="Enter your full name", help="This will be displayed as your display name")
        email = st.text_input("Email", placeholder="Enter your email")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            register_button = st.form_submit_button("Register", use_container_width=True)
        with col2:
            login_button = st.form_submit_button("Switch to Login", use_container_width=True)
    
    if register_button:
        if all([name, email, password, confirm_password]):
            if password == confirm_password:
                try:
                    response = api_client.register(email, password, name)
                    st.success("Registration successful! Please login.")
                    st.session_state.show_register = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Registration failed: {str(e)}")
            else:
                st.error("Passwords do not match")
        else:
            st.error("Please fill in all fields")
    
    if login_button:
        st.session_state.show_register = False
        st.rerun()


def logout_button():
    """Display logout button."""
    if st.button("🚪 Logout", use_container_width=True):
        # Clear session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("Logged out successfully!")
        st.rerun()


def user_info():
    """Display user information."""
    if "user_email" in st.session_state:
        # Get user details
        try:
            user_data = api_client.get_current_user()
            # Display name or email as fallback
            display_name = user_data.get('name') or user_data.get('email', 'User')
            st.info(f"👤 Logged in as: {display_name}")
            
            # Show detailed information
            st.write(f"**Email:** {user_data.get('email', 'N/A')}")
            st.write(f"**Role:** {user_data.get('role', 'User')}")
            st.write(f"**User ID:** {user_data.get('id', 'N/A')}")
        except Exception as e:
            st.warning(f"Could not fetch user details: {str(e)}")
            # Fallback to email if API fails
            st.info(f"👤 Logged in as: {st.session_state.user_email}")


def is_authenticated():
    """Check if user is authenticated."""
    return "access_token" in st.session_state and "user_email" in st.session_state


def show_register():
    """Show register form instead of login form."""
    register_form()


def require_auth():
    """Decorator to require authentication for a function."""
    if not is_authenticated():
        st.error("Please login to access this feature")
        return False
    return True
