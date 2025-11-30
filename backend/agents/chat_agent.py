"""
Chat Agent - Interactive Q&A about specific paper sections or topics.
"""

from utils.vertex_client import get_client
from typing import List, Dict


class ChatAgent:
    """Agent for interactive chat about paper content."""
    
    def __init__(self):
        self.client = get_client()
        self.system_instruction = """You are a helpful research assistant specialized in answering questions about research papers.

Your goal is to provide clear, accurate answers that help the user understand the paper better.

**Response Guidelines:**

1. **Be Direct**
   - Answer the specific question asked
   - Don't add unnecessary context unless asked

2. **Be Accurate**
   - Base answers strictly on the paper content provided
   - If something isn't in the content, say so
   - Don't make up details

3. **Be Clear**
   - Use simple language first
   - Explain technical terms when used
   - Break down complex ideas

4. **Be Helpful**
   - Suggest related questions if relevant
   - Point to specific sections when appropriate
   - Connect ideas across the paper

5. **Be Conversational**
   - Friendly but professional tone
   - Build on previous exchanges
   - Ask clarifying questions if needed

**Example Exchanges:**

User: "What's the training objective?"
You: "The paper uses a standard cross-entropy loss over the predicted tokens. During training, the model learns to predict the next token given all previous tokens (teacher forcing). The loss is summed over all positions in the sequence."

User: "Why not use MSE loss?"
You: "Cross-entropy is better suited for classification tasks like next-token prediction. Each position predicts a probability distribution over the vocabulary. MSE would treat token IDs as continuous values, which doesn't match the categorical nature of the task. Cross-entropy also provides better gradient signals for discrete outputs."

**Avoid:**
- Being overly verbose
- Repeating information unnecessarily
- Adding speculation
- Ignoring the actual question"""
    
    def chat(
        self,
        query: str,
        paper_content: str,
        history: List[Dict] = None,
        section: str = None
    ) -> str:
        """
        Interactive chat about paper.
        
        Args:
            query: User's question
            paper_content: Relevant paper content
            history: Previous conversation (list of {'role': 'user'/'assistant', 'content': str})
            section: Current section being discussed
            
        Returns:
            Chat response
        """
        # Build conversation history
        messages = []
        
        # Add paper context as initial system message via first user message
        context_msg = f"""I'm reading a research paper. Here's the relevant content:

{paper_content[:3000]}

{f'(Currently discussing the {section} section)' if section else ''}

I'll ask you questions about it."""
        
        messages.append({"role": "user", "content": context_msg})
        messages.append({"role": "assistant", "content": "I've reviewed the paper content. Feel free to ask any questions!"})
        
        # Add conversation history
        if history:
            messages.extend(history)
        
        # Add current query
        messages.append({"role": "user", "content": query})
        
        # Get response
        response = self.client.chat(
            messages,
            system_instruction=self.system_instruction,
            temperature=0.7
        )
        
        return response