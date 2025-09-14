import openai
from typing import List, Dict, Any, Optional
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class OpenAIChatService:
    """OpenAI chat service for generating LLM responses."""
    
    def __init__(self):
        self.client = None
        self.llm_model = settings.OPENAI_LLM_MODEL
        
    async def initialize(self):
        """Initialize OpenAI client."""
        try:
            self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            logger.info("OpenAI chat service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise
    
    async def generate_response(
        self, 
        query: str, 
        context: str, 
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """Generate response using OpenAI LLM with retrieved context."""
        try:
            if not self.client:
                await self.initialize()
            
            # Build system prompt
            system_prompt = """You are a helpful assistant that answers questions based on the provided context. 
Use only the information in the context to answer questions. If the context doesn't contain 
relevant information, say "I don't have enough information to answer this question based on the provided documents."

Be concise and accurate in your responses."""
            
            # Build user prompt with context
            user_prompt = f"""Context:
{context}

Question: {query}

Please provide a clear and accurate answer based only on the context above."""
            
            # Prepare messages
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history if provided
            if conversation_history:
                messages.extend(conversation_history)
            
            # Add current query
            messages.append({"role": "user", "content": user_prompt})
            
            # Generate response
            response = await self.client.chat.completions.create(
                model=self.llm_model,
                messages=messages,
                max_tokens=settings.MAX_OUTPUT_TOKENS,
                temperature=settings.TEMPERATURE,
                top_p=settings.TOP_P,
                frequency_penalty=settings.FREQUENCY_PENALTY,
                presence_penalty=settings.PRESENCE_PENALTY
            )
            
            answer = response.choices[0].message.content
            usage = response.usage
            
            return {
                "response": answer,
                "usage": {
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            raise
    
    async def generate_simple_response(self, query: str) -> Dict[str, Any]:
        """Generate a simple response without context (for testing)."""
        try:
            if not self.client:
                await self.initialize()
            
            response = await self.client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": query}
                ],
                max_tokens=settings.MAX_OUTPUT_TOKENS,
                temperature=settings.TEMPERATURE
            )
            
            answer = response.choices[0].message.content
            usage = response.usage
            
            return {
                "response": answer,
                "usage": {
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to generate simple response: {e}")
            raise


# Global chat service instance
openai_chat_service = OpenAIChatService()
