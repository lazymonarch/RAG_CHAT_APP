"""
Email service for sending welcome emails and chat summaries.
"""
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Email configuration - only initialize if properly configured
email_config = None
fm = None

def initialize_email():
    """Initialize email service if configuration is available."""
    global email_config, fm
    
    # Check if email is properly configured
    if (settings.MAIL_USERNAME and 
        settings.MAIL_PASSWORD and 
        settings.MAIL_FROM and
        settings.MAIL_USERNAME != "your-email@gmail.com" and
        settings.MAIL_PASSWORD != "your-app-password"):
        
        email_config = ConnectionConfig(
            MAIL_USERNAME=settings.MAIL_USERNAME,
            MAIL_PASSWORD=settings.MAIL_PASSWORD,
            MAIL_FROM=settings.MAIL_FROM,
            MAIL_PORT=settings.MAIL_PORT,
            MAIL_SERVER=settings.MAIL_SERVER,
            MAIL_STARTTLS=settings.MAIL_TLS,
            MAIL_SSL_TLS=settings.MAIL_SSL,
            USE_CREDENTIALS=settings.USE_CREDENTIALS
        )
        fm = FastMail(email_config)
        logger.info("Email service initialized successfully")
        return True
    else:
        logger.warning("Email not configured - email features will be disabled")
        return False

# Initialize email on import
initialize_email()


async def send_welcome_email(email: str, name: str) -> bool:
    """Send welcome email to newly registered user."""
    try:
        if not fm:
            logger.warning("Email service not configured - skipping welcome email")
            return True  # Return True to not block registration
        
        message = MessageSchema(
            subject="Welcome to RAG Chat!",
            recipients=[email],
            body=f"""
Hi {name},

Welcome to your RAG-powered chat assistant! 🎉

You can now:
• Upload documents (PDF, TXT, DOCX)
• Chat with AI about your content
• Get intelligent answers based on your documents
• Access your chat history anytime

Get started by uploading your first document and asking questions!

Best regards,
The RAG Chat Team
            """,
            subtype="plain"
        )
        
        await fm.send_message(message)
        logger.info(f"Welcome email sent to {email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send welcome email to {email}: {e}")
        return False


async def send_chat_summary_email(
    email: str, 
    name: str, 
    chat_title: str, 
    messages: list,
    summary: str = None
) -> bool:
    """Send chat summary email to user."""
    try:
        if not fm:
            logger.warning("Email service not configured - cannot send chat summary")
            return False
        
        from datetime import datetime
        
        # Get current date for subject
        current_date = datetime.now().strftime("%B %d, %Y")
        
        # Format chat messages for full conversation
        chat_text = "\n".join(
            f"{msg.get('role', 'user').capitalize()}: {msg.get('content', '')}" 
            for msg in messages
        )
        
        # Create email body with the new structured format
        if summary:
            # Parse the AI-generated summary to extract structured information
            structured_summary = await _parse_summary_for_template(summary, chat_title)
            
            body = f"""Hi {name},

Here's a quick summary of your recent chat:

• Topic: {structured_summary['topic']}

• Key Points:
{structured_summary['key_points']}

• Suggested Actions:
{structured_summary['suggested_actions']}

• Recommendation: {structured_summary['recommendation']}

For the full chat, you can view it here: [View Full Chat Link].

– RAG Chat App
            """
        else:
            # Fallback format when no AI summary is available
            body = f"""Hi {name},

Here's your chat conversation for "{chat_title}":

{chat_text}

For the full chat, you can view it here: [View Full Chat Link].

– RAG Chat App
            """
        
        message = MessageSchema(
            subject=f"Your Chat Summary - {current_date}",
            recipients=[email],
            body=body,
            subtype="plain"
        )
        
        await fm.send_message(message)
        logger.info(f"Chat summary email sent to {email} for chat: {chat_title}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send chat summary email to {email}: {e}")
        return False


async def _parse_summary_for_template(summary: str, chat_title: str) -> dict:
    """Parse AI summary into structured template format."""
    try:
        # Use the chat title as the topic if it's meaningful
        topic = chat_title if chat_title and chat_title != "Untitled Conversation" else "General Discussion"
        
        # Split summary into sentences for better parsing
        sentences = [s.strip() for s in summary.split('.') if s.strip()]
        
        # Extract key points (first 2-3 sentences)
        key_points = []
        for i, sentence in enumerate(sentences[:3]):
            if sentence:
                key_points.append(f"   – {sentence}")
        
        # If we have more sentences, use them for suggested actions
        suggested_actions = []
        if len(sentences) > 3:
            for sentence in sentences[3:5]:  # Take next 2 sentences
                if sentence:
                    suggested_actions.append(f"   – {sentence}")
        
        # If no suggested actions from summary, add a generic one
        if not suggested_actions:
            suggested_actions = ["   – Review the full conversation for more details"]
        
        # Add recommendation based on content
        recommendation = "If you need further assistance, feel free to start a new chat session."
        
        # Check if the conversation might need professional advice
        professional_keywords = ['medical', 'health', 'legal', 'financial', 'investment', 'treatment', 'diagnosis']
        if any(keyword in summary.lower() for keyword in professional_keywords):
            recommendation = "If needed, consult a professional for personalized advice."
        
        return {
            'topic': topic,
            'key_points': '\n'.join(key_points) if key_points else "   – Key discussion points from the conversation",
            'suggested_actions': '\n'.join(suggested_actions) if suggested_actions else "   – Review the conversation details",
            'recommendation': recommendation
        }
        
    except Exception as e:
        logger.warning(f"Failed to parse summary for template: {e}")
        # Return fallback structure
        return {
            'topic': chat_title or "General Discussion",
            'key_points': "   – Key discussion points from the conversation",
            'suggested_actions': "   – Review the conversation details",
            'recommendation': "If you need further assistance, feel free to start a new chat session."
        }


async def test_email_connection() -> bool:
    """Test email connection configuration."""
    try:
        # Try to send a test email to verify configuration
        test_message = MessageSchema(
            subject="RAG Chat - Email Test",
            recipients=[settings.MAIL_FROM],  # Send to self
            body="This is a test email to verify email configuration.",
            subtype="plain"
        )
        
        await fm.send_message(test_message)
        logger.info("Email connection test successful")
        return True
        
    except Exception as e:
        logger.error(f"Email connection test failed: {e}")
        return False
