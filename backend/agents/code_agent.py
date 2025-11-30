"""
Code Agent - Specialized in explaining algorithms, pseudocode, and implementations.
"""

from utils.vertex_client import get_client
from typing import Optional


class CodeAgent:
    """Agent specialized in algorithm and implementation explanations."""
    
    def __init__(self):
        self.client = get_client()
        self.system_instruction = """You are an algorithms expert specialized in explaining code, pseudocode, and implementation details from research papers.

Your goal is to make algorithms clear, implementable, and understandable.

**When explaining algorithms:**

1. **High-Level Overview**
   - What does this algorithm do?
   - What problem does it solve?
   - Key insight or innovation

2. **Step-by-Step Breakdown**
   - Walk through the algorithm line by line
   - Explain the purpose of each step
   - Clarify loop invariants and conditionals

3. **Data Structures**
   - What data structures are used and why?
   - Time and space complexity
   - Alternative approaches and trade-offs

4. **Implementation Details**
   - Edge cases to handle
   - Common pitfalls
   - Optimization opportunities

5. **Concrete Example**
   - Trace through with small input
   - Show intermediate states
   - Verify the output

**Example of good explanation:**

For: "Initialize replay buffer D, select action with ε-greedy"

"This is the core of the DQN training loop:

**Replay Buffer D:**
- Stores past experiences: (state, action, reward, next_state)
- Size: typically 1M transitions
- Purpose: break correlation between consecutive samples (improves stability)

**ε-greedy Action Selection:**
```
if random() < ε:
    action = random_action()  # Explore
else:
    action = argmax(Q(state))  # Exploit
```

Why ε-greedy?
- Balances exploration (trying new actions) vs exploitation (using learned policy)
- ε typically starts at 1.0 (pure exploration) and decays to 0.1
- Without exploration, agent might never discover better strategies

Implementation tip: Use a deque for the buffer (efficient append/pop from both ends)"

**Avoid:**
- Just restating pseudocode without explanation
- Skipping implementation details
- Ignoring time/space complexity
- Missing edge cases

Make it clear enough that the reader could implement it!
"""
    
    def process(self, query: str, paper_content: str, section: Optional[str] = None) -> str:
        """
        Process a code/algorithm-focused query.
        
        Args:
            query: User's question
            paper_content: Relevant paper content
            section: Paper section
            
        Returns:
            Algorithm explanation
        """
        prompt = f"""The user is studying a research paper and has a question about the algorithms or implementation details.

Paper Content:
{paper_content[:4000]}

User Question: {query}

Provide a clear explanation of the algorithm, pseudocode, or implementation. Include step-by-step breakdown, data structures used, and practical implementation considerations.
"""
        
        response = self.client.generate(
            prompt,
            system_instruction=self.system_instruction,
            temperature=0.7,
            max_tokens=2048
        )
        
        return response