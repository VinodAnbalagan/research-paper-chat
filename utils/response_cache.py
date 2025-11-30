"""
Response cache for demo mode - pre-computed answers for sample papers.
"""

import json
import os
from typing import Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResponseCache:
    """Manage cached responses for sample papers."""
    
    def __init__(self, cache_dir: str = "data/cached_responses"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        self.caches = {}
        self._load_caches()
    
    def _load_caches(self):
        """Load all cache files."""
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.json'):
                paper_id = filename.replace('.json', '')
                cache_path = os.path.join(self.cache_dir, filename)
                try:
                    with open(cache_path, 'r') as f:
                        self.caches[paper_id] = json.load(f)
                    logger.info(f"Loaded cache for {paper_id}")
                except Exception as e:
                    logger.error(f"Error loading cache {filename}: {e}")
    
    def get_response(
        self,
        paper_id: str,
        query_type: str,
        section: Optional[str] = None,
        query: Optional[str] = None
    ) -> Optional[str]:
        """
        Get cached response.
        
        Args:
            paper_id: ID of the paper (e.g., "attention")
            query_type: Type of query ("explain", "quiz", "chat", etc.)
            section: Paper section if applicable
            query: Specific query if applicable
            
        Returns:
            Cached response or None
        """
        if paper_id not in self.caches:
            return None
        
        cache = self.caches[paper_id]
        
        # Build cache key
        if section and query_type in ["math", "code", "concept"]:
            # Try specific agent type first
            key = f"explain_{section}_{query_type}"
            if key not in cache:
                # Fallback to generic explain
                key = f"explain_{section}"
        elif query_type == "quiz":
            key = f"quiz_{section}" if section else "quiz_general"
        elif query_type == "chat" and query:
            # Simple matching for common questions
            key = self._match_chat_query(cache, query)
        else:
            key = query_type
        
        response = cache.get(key)
        if response:
            logger.info(f"Cache hit: {paper_id}/{key}")
        else:
            logger.info(f"Cache miss: {paper_id}/{key}")
        
        return response
    
    def _match_chat_query(self, cache: Dict, query: str) -> str:
        """Match a chat query to cached responses."""
        query_lower = query.lower()
        
        # Check for exact matches first
        for key in cache.keys():
            if key.startswith("chat_"):
                cached_q = key.replace("chat_", "").replace("_", " ")
                if cached_q in query_lower or query_lower in cached_q:
                    return key
        
        # Return default if no match
        return "chat_general"
    
    def save_cache(self, paper_id: str, cache_data: Dict):
        """Save cache for a paper."""
        cache_path = os.path.join(self.cache_dir, f"{paper_id}.json")
        with open(cache_path, 'w') as f:
            json.dump(cache_data, f, indent=2)
        self.caches[paper_id] = cache_data
        logger.info(f"Saved cache for {paper_id}")
    
    def list_cached_papers(self) -> list:
        """Get list of papers with caches."""
        return list(self.caches.keys())


# Global cache instance
_cache = None

def get_cache() -> ResponseCache:
    """Get or create global cache instance."""
    global _cache
    if _cache is None:
        _cache = ResponseCache()
    return _cache