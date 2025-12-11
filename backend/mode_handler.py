"""
Mode Handler - Manages demo mode (cached) vs live mode (API) switching.
"""

import os
from typing import Dict, Optional
from utils.response_cache import get_cache
from backend.manager import ManagerAgent
from backend.agents.chat_agent import ChatAgent
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModeHandler:
    """Handles switching between demo and live modes."""
    
    def __init__(self, mode: str = None):
        """
        Initialize mode handler.
        
        Args:
            mode: "demo" or "live" (defaults to environment variable APP_MODE)
        """
        self.mode = mode or os.getenv("APP_MODE", "demo")
        self.cache = get_cache()
        self.manager = None  # Lazy initialization
        self.chat_agent = None  # Lazy initialization
        
        logger.info(f"Initialized in {self.mode} mode")
    
    def set_mode(self, mode: str):
        """Switch mode."""
        if mode not in ["demo", "live"]:
            raise ValueError("Mode must be 'demo' or 'live'")
        self.mode = mode
        logger.info(f"Switched to {mode} mode")
    
    def process_query(
        self,
        paper_id: str,
        query: str,
        paper_content: str,
        query_type: str = "explain",
        section: Optional[str] = None
    ) -> Dict:
        """
        Process a query in either demo or live mode.
        
        Args:
            paper_id: ID of the paper (e.g., "attention")
            query: User's question
            paper_content: Relevant paper content
            query_type: "explain", "quiz", "chat", etc.
            section: Paper section if applicable
            
        Returns:
            Dict with 'response', 'mode', 'agent' (if live)
        """
        # Try demo mode first if enabled
        if self.mode == "demo":
            cached_response = self.cache.get_response(
                paper_id,
                query_type,
                section,
                query
            )
            
            if cached_response:
                return {
                    "response": cached_response,
                    "mode": "demo",
                    "cached": True
                }
            
            # If no cache hit, provide helpful guidance
            logger.warning(f"No cached response for {paper_id}/{query_type}")
            
            if paper_id == "attention":
                return {
                    "response": "This paper has comprehensive demo content available! Try clicking the buttons above to see pre-computed analysis, or switch to Live mode to ask custom questions with your own API key.",
                    "mode": "demo",
                    "cached": False
                }
            else:
                return {
                    "response": f"Demo responses are currently only available for 'Attention Is All You Need'. For the {paper_id} paper, please switch to Live mode and add your Google AI Studio API key to get AI-powered analysis.",
                    "mode": "demo", 
                    "cached": False
                }
        
        # Live mode - use actual agents
        if not self.manager:
            try:
                self.manager = ManagerAgent()
            except ValueError as e:
                # API key not configured
                return {
                    "response": "⚠️ API key not configured. Please add your Google AI Studio API key in the sidebar to use Live mode.",
                    "mode": "live",
                    "cached": False,
                    "error": str(e)
                }
        
        result = self.manager.process_query(
            query,
            paper_content,
            section,
            agent_type=query_type if query_type != "explain" else None
        )
        
        return {
            "response": result['response'],
            "mode": "live",
            "agent": result['agent'],
            "reasoning": result['reasoning'],
            "cached": False
        }
    
    def chat(
        self,
        paper_id: str,
        query: str,
        paper_content: str,
        history: list = None,
        section: Optional[str] = None
    ) -> Dict:
        """
        Handle chat queries.
        
        Args:
            paper_id: Paper ID
            query: User's question
            paper_content: Paper content
            history: Conversation history
            section: Current section
            
        Returns:
            Dict with response
        """
        # Try demo mode cache first
        if self.mode == "demo":
            cached_response = self.cache.get_response(
                paper_id,
                "chat",
                section,
                query
            )
            
            if cached_response:
                return {
                    "response": cached_response,
                    "mode": "demo",
                    "cached": True
                }
            
            # For attention paper, provide helpful guidance
            if paper_id == "attention":
                return {
                    "response": "For the best demo experience with 'Attention Is All You Need', try clicking one of the sample questions above! They provide comprehensive answers about the Transformer architecture. For custom questions, switch to Live mode with your own API key.",
                    "mode": "demo",
                    "cached": False
                }
            else:
                return {
                    "response": f"Chat responses are currently only available in demo mode for 'Attention Is All You Need'. For the {paper_id} paper, please switch to Live mode and add your API key.",
                    "mode": "demo",
                    "cached": False
                }
        
        # Live mode - use chat agent
        if not self.chat_agent:
            self.chat_agent = ChatAgent()
        
        response = self.chat_agent.chat(
            query,
            paper_content,
            history,
            section
        )
        
        return {
            "response": response,
            "mode": "live",
            "cached": False
        }