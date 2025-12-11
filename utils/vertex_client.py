"""
Vertex AI / Gemini API client wrapper.
"""

import os
import google.generativeai as genai
from typing import Optional, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeminiClient:
    """Wrapper for Google Gemini API."""
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-2.0-flash"):
        """
        Initialize Gemini client.
        
        Args:
            api_key: Google API key (or loads from environment)
            model_name: Model to use
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key or self.api_key == "your-api-key-here":
            raise ValueError("GOOGLE_API_KEY not found in environment")
        
        genai.configure(api_key=self.api_key)
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)
        
        logger.info(f"Initialized Gemini client with model: {model_name}")
    
    def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 8192
    ) -> str:
        """
        Generate response from Gemini.
        
        Args:
            prompt: User prompt
            system_instruction: System instruction for the model
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text
        """
        try:
            # Create model with system instruction if provided
            if system_instruction:
                model = genai.GenerativeModel(
                    self.model_name,
                    system_instruction=system_instruction
                )
            else:
                model = self.model
            
            # Configure safety settings for academic/technical content
            from google.generativeai.types import HarmCategory, HarmBlockThreshold
            
            safety_settings = {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
            
            # Generate response
            response = model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                ),
                safety_settings=safety_settings
            )
            
            # Check if response was blocked
            if not response.candidates:
                logger.warning("Response was blocked by safety filters")
                return "I apologize, but I cannot generate a response for this content due to safety filters. Please try rephrasing your question or selecting a different section."
            
            # Check finish reason
            finish_reason = response.candidates[0].finish_reason
            if finish_reason == 2:  # SAFETY
                logger.warning("Response blocked due to safety concerns")
                return "I apologize, but this content triggered safety filters. Please try a different section or rephrase your question."
            elif finish_reason == 3:  # RECITATION
                logger.warning("Response blocked due to recitation concerns")
                return "I apologize, but I cannot provide this response due to content policy. Please try a different approach."
            
            # Try to get text, with fallback
            try:
                return response.text
            except ValueError as ve:
                logger.error(f"Could not extract text from chat response: {ve}")
                return "I apologize, but I encountered an issue generating a response. Please try rephrasing your question."
            except AttributeError:
                logger.error("Response has no text attribute")
                return "I apologize, but I received an invalid response. Please try again."
            except ValueError as ve:
                logger.error(f"Could not extract text from response: {ve}")
                return "I apologize, but I encountered an issue generating a response. Please try again with a different section or question."
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
    
    def chat(
        self,
        messages: list,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        """
        Multi-turn chat with Gemini.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            system_instruction: System instruction
            temperature: Sampling temperature
            
        Returns:
            Generated response
        """
        try:
            # Create chat session
            if system_instruction:
                model = genai.GenerativeModel(
                    self.model_name,
                    system_instruction=system_instruction
                )
            else:
                model = self.model
            
            # Build history in Gemini format (exclude last user message)
            history = []
            for msg in messages[:-1]:
                role = "user" if msg['role'] == 'user' else "model"
                history.append({
                    "role": role,
                    "parts": [msg['content']]
                })
            
            # Start chat with history
            chat = model.start_chat(history=history)
            
            # Configure safety settings for academic/technical content
            from google.generativeai.types import HarmCategory, HarmBlockThreshold
            
            safety_settings = {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
            
            # Send last message and get response
            response = chat.send_message(
                messages[-1]['content'],
                generation_config=genai.GenerationConfig(
                    temperature=temperature,
                ),
                safety_settings=safety_settings
            )
            
            # Check if response was blocked
            if not response.candidates:
                logger.warning("Chat response was blocked by safety filters")
                return "I apologize, but I cannot generate a response for this content due to safety filters. Please try rephrasing your question."
            
            # Check finish reason
            finish_reason = response.candidates[0].finish_reason
            if finish_reason == 2:  # SAFETY
                logger.warning("Chat response blocked due to safety concerns")
                return "I apologize, but this content triggered safety filters. Please rephrase your question."
            
            # Try to get text, with fallback
            try:
                return response.text
            except ValueError as ve:
                logger.error(f"Could not extract text from chat response: {ve}")
                return "I apologize, but I encountered an issue generating a response. Please try rephrasing your question."
            
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            # Handle specific API errors gracefully
            import google.api_core.exceptions
            if isinstance(e, google.api_core.exceptions.InternalServerError):
                return "I apologize, but the AI service is temporarily unavailable. This is usually a brief issue. Please try again in a moment."
            elif isinstance(e, google.api_core.exceptions.ResourceExhausted):
                return "I apologize, but we've hit the API rate limit. Please wait a moment and try again."
            else:
                # For other errors, provide a generic message
                return "I apologize, but I encountered an unexpected error. Please try rephrasing your question or try again later."


# Global client instance
_client = None

def get_client(model_name: str = "gemini-2.0-flash") -> GeminiClient:
    """Get or create global client instance."""
    global _client
    if _client is None:
        _client = GeminiClient(model_name=model_name)
    return _client