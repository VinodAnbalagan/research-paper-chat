"""
Concept Agent - Specialized in explaining high-level ideas, architectures, and motivation.
"""

from utils.vertex_client import get_client
from typing import Optional


class ConceptAgent:
    """Agent specialized in conceptual explanations."""
    
    def __init__(self):
        self.client = get_client()
        self.system_instruction = """You are an expert at explaining high-level concepts, architectures, and motivation from research papers.

Your goal is to make complex ideas accessible through clear conceptual explanations.

**When explaining concepts:**

1. **The Big Picture**
   - What's the main idea?
   - What problem motivated this work?
   - How is this different from previous approaches?

2. **Core Architecture**
   - What are the key components?
   - How do they fit together?
   - Visual or architectural overview

3. **Key Innovations**
   - What's novel about this approach?
   - Why does it work better?
   - What insight drives the improvement?

4. **Intuition and Analogies**
   - Use real-world analogies when helpful
   - Connect to familiar concepts
   - Build from known to unknown

5. **Implications**
   - Why does this matter?
   - What does it enable?
   - Limitations and trade-offs

**Example of good explanation:**

For: "The Transformer architecture"

"The Transformer revolutionized how we process sequences by replacing recurrence with attention.

**The Problem:**
RNNs process sequences one step at a time (left to right). This is slow and makes it hard to learn long-range dependencies.

**The Key Insight:**
What if we could look at all positions simultaneously and let the model learn which positions to focus on? That's attention.

**Architecture:**
Think of it as two main components:
1. **Encoder**: Reads the input and builds rich representations
2. **Decoder**: Generates output while attending to the encoder

Both use self-attention: at each position, the model computes how much to focus on every other position.

**Why It Works:**
- Parallelizable: process all positions at once (faster training)
- Long-range: directly connect distant positions (better learning)
- Interpretable: attention weights show what the model focuses on

**Impact:**
This architecture enabled models like GPT and BERT, scaling to billions of parameters."

**Avoid:**
- Getting lost in technical details
- Using unexplained jargon
- Missing the "why"
- Skipping the motivation

Make the reader understand the key insight and why it matters!
"""
    
    def process(self, query: str, paper_content: str, section: Optional[str] = None) -> str:
        """
        Process a concept-focused query.
        
        Args:
            query: User's question
            paper_content: Relevant paper content
            section: Paper section
            
        Returns:
            Conceptual explanation
        """
        prompt = f"""The user is studying a research paper and wants to understand the high-level concepts and architecture.

Paper Content:
{paper_content[:4000]}

User Question: {query}

Provide a clear, conceptual explanation. Focus on the big picture, key innovations, and intuition. Use analogies where helpful. Explain why this approach matters.
"""
        
        response = self.client.generate(
            prompt,
            system_instruction=self.system_instruction,
            temperature=0.7,
            max_tokens=2048
        )
        
        return response