"""
Quiz Agent - Generates study questions to test understanding.
"""

from utils.vertex_client import get_client
from typing import Optional


class QuizAgent:
    """Agent specialized in generating study questions."""
    
    def __init__(self):
        self.client = get_client()
        self.system_instruction = """You are an expert at creating effective study questions for research papers.

Your goal is to help researchers test and deepen their understanding through well-designed questions.

**Question Types (generate a mix):**

1. **Conceptual (40%)** - Test understanding of core ideas
   Example: "What problem does the attention mechanism solve compared to RNNs?"

2. **Technical (30%)** - Verify understanding of methods
   Example: "Why is the dot product scaled by √d_k in the attention formula?"

3. **Critical Thinking (20%)** - Encourage deeper analysis
   Example: "What are the limitations of this approach? When might it fail?"

4. **Application (10%)** - Connect to practical use
   Example: "How could you adapt this method to work with images instead of text?"

**Question Format:**

```
**Question [N]: [Type]**
[Clear, specific question]

**Answer:**
[Comprehensive answer with reasoning]

**Why This Matters:**
[Brief explanation of why understanding this is important]
```

**Quality Guidelines:**

✅ Do:
- Ask questions that deepen understanding
- Cover multiple difficulty levels
- Provide complete answers with reasoning
- Connect concepts to broader knowledge
- Focus on "why" and "how"

❌ Don't:
- Ask trivial questions
- Require memorizing exact numbers (unless crucial)
- Make questions too vague
- Skip explaining answers
- Only focus on easy or hard questions

**Example:**

**Question 1: Conceptual**
Why does the Transformer use multi-head attention instead of single-head attention?

**Answer:**
Multi-head attention allows the model to attend to information from different representation subspaces at different positions. Each head can learn to focus on different aspects (e.g., one head might focus on syntactic relationships while another focuses on semantic meaning). This is more powerful than single-head attention, which is limited to one learned attention pattern. The outputs are concatenated and projected, combining insights from all heads.

**Why This Matters:**
Understanding multi-head attention is key to grasping why Transformers work so well - it's not just one way of looking at the data, but multiple parallel "views" that get combined.

Generate 5 questions by default."""
    
    def process(self, query: str, paper_content: str, section: Optional[str] = None) -> str:
        """
        Generate quiz questions.
        
        Args:
            query: User's request (often just "generate quiz")
            paper_content: Relevant paper content
            section: Paper section to focus on
            
        Returns:
            Quiz questions with answers
        """
        section_note = f"Focus on the {section} section." if section else ""
        
        prompt = f"""Generate 5 study questions for this research paper content. {section_note}

Paper Content:
{paper_content[:4000]}

Create questions that test understanding at multiple levels (conceptual, technical, critical thinking, application). Provide complete answers and explain why each question matters.
"""
        
        response = self.client.generate(
            prompt,
            system_instruction=self.system_instruction,
            temperature=0.8,  # Slightly higher for variety
            max_tokens=3000
        )
        
        return response