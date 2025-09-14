"""
Authentication Components
"""
import streamlit as st
from utils.api_client import api_client


def login_form():
    """Display login form."""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1rem; 
                border-radius: 10px; margin-bottom: 1rem; text-align: center;">
        <h3 style="color: white; margin: 0;">🔐 Welcome Back</h3>
        <p style="color: #f0f0f0; margin: 0.5rem 0 0 0; font-size: 0.9rem;">Sign in to your account</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        email = st.text_input(
            "📧 Email Address", 
            placeholder="Enter your email address",
            help="Enter your registered email address"
        )
        password = st.text_input(
            "🔒 Password", 
            type="password", 
            placeholder="Enter your password",
            help="Enter your account password"
        )
        
        col1, col2 = st.columns([1, 1])
        with col1:
            login_button = st.form_submit_button(
                "🚀 Login", 
                use_container_width=True,
                type="primary"
            )
        with col2:
            register_button = st.form_submit_button(
                "📝 Register", 
                use_container_width=True,
                type="secondary"
            )
    
    if login_button:
        if email and password:
            with st.spinner("Signing you in..."):
                try:
                    response = api_client.login(email, password)
                    st.session_state.access_token = response["access_token"]
                    st.session_state.user_email = email
                    st.session_state.user_id = None  # Will be fetched later
                    st.success("🎉 Login successful! Welcome back!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Login failed: {str(e)}")
        else:
            st.error("⚠️ Please fill in all fields")
    
    if register_button:
        st.session_state.show_register = True
        st.rerun()


def register_form():
    """Display registration form."""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); padding: 1rem; 
                border-radius: 10px; margin-bottom: 1rem; text-align: center;">
        <h3 style="color: white; margin: 0;">📝 Create Account</h3>
        <p style="color: #f0f0f0; margin: 0.5rem 0 0 0; font-size: 0.9rem;">Join our AI-powered community</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("register_form"):
        name = st.text_input(
            "👤 Full Name", 
            placeholder="Enter your full name", 
            help="This will be displayed as your display name in the app"
        )
        email = st.text_input(
            "📧 Email Address", 
            placeholder="Enter your email address",
            help="We'll use this for account verification and notifications"
        )
        password = st.text_input(
            "🔒 Password", 
            type="password", 
            placeholder="Create a strong password",
            help="Use at least 8 characters with letters and numbers"
        )
        confirm_password = st.text_input(
            "🔒 Confirm Password", 
            type="password", 
            placeholder="Confirm your password",
            help="Re-enter your password to confirm"
        )
        
        col1, col2 = st.columns([1, 1])
        with col1:
            register_button = st.form_submit_button(
                "🚀 Create Account", 
                use_container_width=True,
                type="primary"
            )
        with col2:
            login_button = st.form_submit_button(
                "🔐 Login", 
                use_container_width=True,
                type="secondary"
            )
    
    if register_button:
        if all([name, email, password, confirm_password]):
            if password == confirm_password:
                with st.spinner("Creating your account..."):
                    try:
                        response = api_client.register(email, password, name)
                        st.success("🎉 Registration successful! You can now login.")
                        st.session_state.show_register = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Registration failed: {str(e)}")
            else:
                st.error("⚠️ Passwords do not match. Please try again.")
        else:
            st.error("⚠️ Please fill in all fields")
    
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
