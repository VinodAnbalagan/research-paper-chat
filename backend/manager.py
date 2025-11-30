"""
Manager Agent - Orchestrates routing to specialized agents.
"""

import re
from typing import Dict, Optional
from utils.vertex_client import get_client
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ManagerAgent:
    """Manager agent that routes queries to specialized agents."""
    
    def __init__(self):
        self.client = get_client()
        
        # Routing patterns
        self.math_patterns = [
            r'equation', r'formula', r'proof', r'theorem', r'mathematical',
            r'derive', r'calculation', r'\$.*\$', r'\\begin\{equation\}'
        ]
        
        self.code_patterns = [
            r'algorithm', r'implementation', r'code', r'pseudocode',
            r'procedure', r'function', r'class', r'def ', r'for loop'
        ]
        
        self.quiz_patterns = [
            r'quiz', r'question', r'test', r'study', r'exam'
        ]
    
    def route_query(
        self,
        query: str,
        paper_content: str,
        section: Optional[str] = None
    ) -> Dict:
        """
        Analyze query and route to appropriate agent.
        
        Args:
            query: User's question
            paper_content: Relevant paper content
            section: Paper section if specified
            
        Returns:
            Dict with 'agent' (which agent to use) and 'reasoning'
        """
        query_lower = query.lower()
        content_lower = (paper_content[:1000]).lower()  # Check first 1000 chars
        
        # Check for quiz generation
        if any(re.search(pattern, query_lower) for pattern in self.quiz_patterns):
            return {
                "agent": "quiz",
                "reasoning": "User wants to generate study questions"
            }
        
        # Check if content or query involves math
        has_math = any(re.search(pattern, query_lower + content_lower) 
                      for pattern in self.math_patterns)
        
        # Check if content or query involves code
        has_code = any(re.search(pattern, query_lower + content_lower)
                      for pattern in self.code_patterns)
        
        # Routing logic
        if has_math and has_code:
            # Use LLM to decide
            routing_prompt = f"""Given this query and content, decide if it's primarily about:
1. MATH (equations, proofs, mathematical concepts)
2. CODE (algorithms, implementation, pseudocode)
3. CONCEPT (high-level ideas, architecture, motivation)

Query: {query}
Content preview: {paper_content[:500]}

Respond with just one word: MATH, CODE, or CONCEPT"""
            
            try:
                decision = self.client.generate(
                    routing_prompt,
                    temperature=0.1,
                    max_tokens=10
                ).strip().upper()
                
                if decision == "MATH":
                    return {"agent": "math", "reasoning": "Content involves mathematical analysis"}
                elif decision == "CODE":
                    return {"agent": "code", "reasoning": "Content involves algorithms/implementation"}
                else:
                    return {"agent": "concept", "reasoning": "Content is conceptual"}
                    
            except:
                # Fallback to concept
                return {"agent": "concept", "reasoning": "Default to conceptual explanation"}
        
        elif has_math:
            return {"agent": "math", "reasoning": "Content involves mathematics"}
        
        elif has_code:
            return {"agent": "code", "reasoning": "Content involves code/algorithms"}
        
        else:
            return {"agent": "concept", "reasoning": "Content is conceptual"}
    
    def process_query(
        self,
        query: str,
        paper_content: str,
        section: Optional[str] = None,
        agent_type: Optional[str] = None
    ) -> Dict:
        """
        Process a query - route and get response.
        
        Args:
            query: User's question
            paper_content: Relevant paper content
            section: Paper section
            agent_type: Force specific agent (optional)
            
        Returns:
            Dict with 'agent', 'response', 'reasoning'
        """
        # Determine which agent to use
        if agent_type:
            routing = {"agent": agent_type, "reasoning": "User specified"}
        else:
            routing = self.route_query(query, paper_content, section)
        
        logger.info(f"Routing to {routing['agent']} agent: {routing['reasoning']}")
        
        # Import and use the appropriate agent
        from backend.agents.math_agent import MathAgent
        from backend.agents.code_agent import CodeAgent
        from backend.agents.concept_agent import ConceptAgent
        from backend.agents.quiz_agent import QuizAgent
        
        if routing['agent'] == 'math':
            agent = MathAgent()
        elif routing['agent'] == 'code':
            agent = CodeAgent()
        elif routing['agent'] == 'quiz':
            agent = QuizAgent()
        else:
            agent = ConceptAgent()
        
        # Get response from agent
        response = agent.process(query, paper_content, section)
        
        return {
            "agent": routing['agent'],
            "reasoning": routing['reasoning'],
            "response": response
        }