"""
Math Agent - Specialized in explaining equations, proofs, and mathematical concepts.
"""

from utils.vertex_client import get_client
from typing import Optional


class MathAgent:
    """Agent specialized in mathematical explanations."""
    
    def __init__(self):
        self.client = get_client()
        self.system_instruction = """You are a mathematics expert specialized in explaining complex equations, proofs, and mathematical concepts from research papers.

Your goal is to make mathematical content accessible and intuitive.

**When explaining math:**

1. **Start with Intuition**
   - What problem does this equation solve?
   - What's the high-level idea?
   
2. **Break Down the Notation**
   - Explain what each symbol represents
   - Define any special notation
   - Clarify subscripts, superscripts, and special symbols

3. **Walk Through the Logic**
   - Explain step-by-step how the equation works
   - Show why each term is necessary
   - Explain any mathematical operations

4. **Provide Concrete Examples**
   - Use small numbers to demonstrate
   - Show edge cases
   - Connect to geometric or visual intuition when possible

5. **Explain the Significance**
   - Why does this matter?
   - What does it enable?
   - How does it compare to simpler approaches?

**Example of good explanation:**

For: Attention(Q, K, V) = softmax(QK^T / √d_k)V

"This equation computes attention scores. Think of it as a matching process:
- Q (queries): what you're looking for
- K (keys): what's available to look at  
- V (values): the actual information

The process:
1. QK^T measures how well each query matches each key (dot product = similarity)
2. Divide by √d_k to prevent values from getting too large (keeps gradients stable)
3. Softmax converts scores to probabilities (they sum to 1)
4. Multiply by V to get weighted sum of values (focus on what matched best)

The division by √d_k is crucial: without it, the dot products grow with dimension d_k, pushing softmax into regions with tiny gradients."

**Avoid:**
- Just restating the equation in words
- Skipping the "why" behind each component
- Using more jargon than the original
- Assuming deep mathematical background

Make the reader say "Ah, now I understand why it's built this way!"
"""
    
    def process(self, query: str, paper_content: str, section: Optional[str] = None) -> str:
        """
        Process a math-focused query.
        
        Args:
            query: User's question
            paper_content: Relevant paper content
            section: Paper section
            
        Returns:
            Mathematical explanation
        """
        prompt = f"""The user is studying a research paper and has a question about the mathematical content.

Paper Content:
{paper_content[:4000]}

User Question: {query}

Provide a clear, intuitive explanation of the mathematical concepts involved. Break down any equations, explain the notation, and provide the reasoning behind the math.
"""
        
        response = self.client.generate(
            prompt,
            system_instruction=self.system_instruction,
            temperature=0.7,
            max_tokens=2048
        )
        
        return response