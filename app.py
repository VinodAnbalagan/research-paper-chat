"""
Research Paper Chat - Streamlit App
Multi-agent system for understanding research papers
"""

import streamlit as st
import os
from dotenv import load_dotenv
import yaml
from pathlib import Path

# Load environment variables
load_dotenv()

# IMPORTANT: For Streamlit Cloud, also load from st.secrets
# Streamlit Cloud doesn't use .env files, it uses secrets
if not os.getenv("GOOGLE_API_KEY"):
    try:
        # Try to load from Streamlit secrets
        if "GOOGLE_API_KEY" in st.secrets:
            os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
        if "APP_MODE" in st.secrets:
            os.environ["APP_MODE"] = st.secrets["APP_MODE"]
    except:
        # If secrets don't exist (local dev without secrets.toml), that's ok
        pass

# Import our modules
from tools.pdf_parser import PaperParser
from backend.mode_handler import ModeHandler

# Page config
st.set_page_config(
    page_title="Research Paper Chat",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern, minimalistic design
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #4F46E5;
        --secondary-color: #818CF8;
        --background-color: #F9FAFB;
        --text-color: #1F2937;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Modern card styling */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 12px 24px;
        background-color: #F3F4F6;
        color: #6B7280;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Chat message styling */
    .stChatMessage {
        border-radius: 12px;
        padding: 16px;
        margin: 8px 0;
        background-color: #F9FAFB;
        border: 1px solid #E5E7EB;
    }
    
    /* File uploader styling */
    .stFileUploader {
        border: 2px dashed #D1D5DB;
        border-radius: 12px;
        padding: 24px;
        background-color: #F9FAFB;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #F9FAFB 0%, #F3F4F6 100%);
    }
    
    /* Info boxes */
    .stAlert {
        border-radius: 8px;
        border-left: 4px solid #667eea;
    }
    
    /* Headers */
    h1 {
        color: #1F2937;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    
    h2, h3 {
        color: #374151;
        font-weight: 600;
    }
    
    /* Caption text */
    .stCaption {
        color: #6B7280;
        font-size: 0.875rem;
    }
</style>
""", unsafe_allow_html=True)

# Load configuration
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Initialize session state
if "mode_handler" not in st.session_state:
    st.session_state.mode_handler = ModeHandler()

if "current_paper" not in st.session_state:
    st.session_state.current_paper = None

if "paper_parser" not in st.session_state:
    st.session_state.paper_parser = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "selected_section" not in st.session_state:
    st.session_state.selected_section = None

# Sidebar
with st.sidebar:
    # Header with icon
    st.markdown("### 📚 Research Paper Chat")
    st.markdown("*AI-Powered Paper Analysis*")
    st.markdown("---")
    
    # Mode selection
    st.markdown("#### 🎮 Choose Mode")
    
    mode_options = {
        "demo": "🎯 Demo Mode (No API Key Needed)",
        "live": "⚡ Live Mode (Bring Your Own Key)"
    }
    
    selected_mode = st.radio(
        "Select Mode:", 
        list(mode_options.keys()), 
        format_func=lambda x: mode_options[x],
        index=0  # Default to demo mode
    )
    
    # Set mode based on selection
    if st.session_state.mode_handler.mode != selected_mode:
        st.session_state.mode_handler.set_mode(selected_mode)
    
    # Paper selection based on mode
    if selected_mode == "demo":
        st.markdown("#### 📚 Sample Papers")
        
        sample_papers = config['sample_papers']
        paper_titles = [f"{p['title']} ({p['year']})" for p in sample_papers]
        
        selected_idx = st.selectbox(
            "Choose a paper:",
            range(len(paper_titles)),
            format_func=lambda i: paper_titles[i]
        )
        
        if st.button("📖 Load Sample Paper", use_container_width=True):
            paper = sample_papers[selected_idx]
            paper_path = f"data/sample_papers/{paper['file']}"
            
            if os.path.exists(paper_path):
                st.session_state.current_paper = paper
                st.session_state.paper_parser = PaperParser(paper_path)
                st.session_state.chat_history = []
                st.success("✓ Sample paper loaded!")
            else:
                st.error("❌ Sample paper not found")
    
    else:  # Live mode
        st.markdown("#### 📄 Upload Your Paper")
        
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=['pdf'],
            help="Upload any research paper in PDF format",
            label_visibility="collapsed"
        )
        
        if uploaded_file:
            # Check if API key is available
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key or api_key == "your-api-key-here":
                st.error("⚠️ Please add your API key above first")
            else:
                if st.button("🚀 Process Paper", use_container_width=True):
                    with st.spinner("Processing..."):
                        # Save temporarily
                        temp_path = f"temp_{uploaded_file.name}"
                        with open(temp_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        
                        st.session_state.current_paper = {
                            "id": "uploaded",
                            "title": uploaded_file.name,
                            "file": temp_path
                        }
                        st.session_state.paper_parser = PaperParser(temp_path)
                        st.session_state.chat_history = []
                        st.success("✓ Paper loaded successfully!")
    
    st.markdown("---")
    
    # API Key Configuration for Live Mode
    if selected_mode == "live":
        st.markdown("#### 🔑 Your API Key")
        st.markdown("Get free key: [Google AI Studio →](https://aistudio.google.com/app/apikey)")
        
        user_api_key = st.text_input(
            "Paste your API key here:",
            type="password",
            help="Your key is never stored. Only used in your browser session.",
            placeholder="AIzaSy..."
        )
        
        if user_api_key:
            os.environ["GOOGLE_API_KEY"] = user_api_key
            st.success("✅ API Key Connected!")
            st.caption("You can now upload custom PDFs")
        else:
            st.warning("⚠️ Live mode requires an API key")
            st.caption("Free tier: 15 req/min, 1500 req/day")
    
    elif selected_mode == "demo":
        st.markdown("#### 🎯 Demo Mode Active")
        st.success("✅ Using Pre-computed Responses")
        st.caption("Try with sample papers below")
    
    st.markdown("---")
    
    # Current paper info
    if st.session_state.current_paper:
        st.markdown("#### 📖 Current Paper")
        st.info(st.session_state.current_paper['title'])
    
    st.markdown("---")
    
    st.markdown("---")
    
    # Footer
    st.caption("Built for Google's 5-Day AI Agents Intensive")
    st.caption("© 2024 Research Paper Chat")

# Main content area
if st.session_state.current_paper is None:
    # Hero section
    st.markdown("<h1 style='text-align: center; margin-bottom: 0;'>📚 Research Paper Chat</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2rem; color: #6B7280; margin-top: 0;'>AI-Powered Research Paper Analysis</p>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Two modes explanation
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 24px; border-radius: 12px; color: white; text-align: center;'>
            <h3 style='color: white; margin: 0;'>🎯 Demo Mode</h3>
            <p style='margin: 8px 0 0 0; opacity: 0.9;'>Try with 3 sample papers<br>No API key needed</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 24px; border-radius: 12px; color: white; text-align: center;'>
            <h3 style='color: white; margin: 0;'>⚡ Live Mode</h3>
            <p style='margin: 8px 0 0 0; opacity: 0.9;'>Upload any paper<br>Bring your own API key</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Features
    st.markdown("### 🤖 AI Agents")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🧮 Math Agent**  \nEquations & Proofs")
    
    with col2:
        st.markdown("**💻 Code Agent**  \nAlgorithms & Implementation")
    
    with col3:
        st.markdown("**🎯 Concept Agent**  \nIdeas & Architecture")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Call to action
    st.info("👈 **Get Started:** Choose a mode in the sidebar!")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # API key info
    st.markdown("""
    <div style='text-align: center; padding: 24px; background-color: #F9FAFB; border-radius: 12px;'>
        <p style='color: #6B7280; margin: 0;'>Need an API key for Live mode?</p>
        <p style='color: #4F46E5; margin: 8px 0 0 0;'><a href="https://aistudio.google.com/app/apikey" target="_blank">Get Free Google AI Studio Key →</a></p>
        <p style='color: #9CA3AF; margin: 4px 0 0 0; font-size: 0.875rem;'>15 requests/min, 1500/day - completely free!</p>
    </div>
    """, unsafe_allow_html=True)
    


else:
    # Paper is loaded
    paper = st.session_state.current_paper
    parser = st.session_state.paper_parser
    
    st.title(f"{paper['title']}")
    
    # Show mode indicator
    if st.session_state.mode_handler.mode == "demo":
        if paper['id'] == "attention":
            st.success("Demo Mode Active: Full analysis available for 'Attention Is All You Need' - click buttons below to explore!")
        else:
            st.warning(f"Demo Mode: Limited content available for this paper. Switch to Live mode for full AI analysis.")
    
    # Extract sections if not already done
    if not parser.sections:
        with st.spinner("Extracting paper sections..."):
            parser.extract_sections()
    
    # Tabs for different actions
    tab1, tab2, tab3 = st.tabs(["Explain", "Chat", "Quiz"])
    
    with tab1:
        st.markdown("### AI Agents")
        
        # Check if we're in demo mode and show demo content
        if st.session_state.mode_handler.mode == "demo" and paper['id'] == "attention":
            st.markdown("**Demo Mode**: Click to see pre-computed analysis of 'Attention Is All You Need'")
            st.markdown("<br>", unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("""
                <div style='text-align: center; padding: 12px; background-color: #F9FAFB; border-radius: 8px; margin-bottom: 12px;'>
                    <h4 style='margin: 0; color: #4F46E5;'>Math Agent</h4>
                    <p style='margin: 4px 0 0 0; font-size: 0.875rem; color: #6B7280;'>Equations & Proofs</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("Show Math Analysis", use_container_width=True, key="math_btn"):
                    st.markdown("---")
                    st.markdown("#### Mathematical Analysis")
                    st.markdown("""
**Core Mathematical Innovation: Scaled Dot-Product Attention**

The paper introduces the fundamental attention mechanism:

```
Attention(Q, K, V) = softmax(QK^T / √d_k)V
```

**Breaking it down:**
- **Q** (queries), **K** (keys), **V** (values) are learned linear projections
- **QK^T** computes similarity scores between all query-key pairs
- **√d_k** scaling prevents gradients from vanishing in high dimensions
- **softmax** converts scores to probabilities
- Final multiplication with **V** produces weighted outputs

**Multi-Head Attention Mathematics:**
```
MultiHead(Q,K,V) = Concat(head_1,...,head_h)W^O
where head_i = Attention(QW_i^Q, KW_i^K, VW_i^V)
```

**Key Mathematical Properties:**
1. **Permutation Equivariance**: Attention is invariant to input order
2. **Quadratic Complexity**: O(n²d) for sequence length n
3. **Parallel Computation**: All positions computed simultaneously

**Positional Encoding Formula:**
```
PE(pos, 2i) = sin(pos/10000^(2i/d_model))
PE(pos, 2i+1) = cos(pos/10000^(2i/d_model))
```

This sinusoidal encoding allows the model to learn relative positions.
                    """)
                    st.caption("Generated by Math Agent")
            
            with col2:
                st.markdown("""
                <div style='text-align: center; padding: 12px; background-color: #F9FAFB; border-radius: 8px; margin-bottom: 12px;'>
                    <h4 style='margin: 0; color: #4F46E5;'>Code Agent</h4>
                    <p style='margin: 4px 0 0 0; font-size: 0.875rem; color: #6B7280;'>Algorithms & Implementation</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("Show Algorithm Analysis", use_container_width=True, key="code_btn"):
                    st.markdown("---")
                    st.markdown("#### Algorithm Analysis")
                    st.markdown("""
**Core Algorithm: Self-Attention Mechanism**

```python
def scaled_dot_product_attention(Q, K, V, mask=None):
    # Compute attention scores
    scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(d_k)
    
    # Apply mask if provided (for decoder)
    if mask is not None:
        scores = scores.masked_fill(mask == 0, -1e9)
    
    # Apply softmax
    attention_weights = F.softmax(scores, dim=-1)
    
    # Apply attention to values
    output = torch.matmul(attention_weights, V)
    return output, attention_weights
```

**Multi-Head Implementation:**
```python
class MultiHeadAttention(nn.Module):
    def __init__(self, d_model, num_heads):
        super().__init__()
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)
    
    def forward(self, query, key, value, mask=None):
        batch_size = query.size(0)
        
        # Linear projections and reshape for multi-head
        Q = self.W_q(query).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        K = self.W_k(key).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        V = self.W_v(value).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        
        # Apply attention
        attention_output, _ = scaled_dot_product_attention(Q, K, V, mask)
        
        # Concatenate heads and apply final linear layer
        attention_output = attention_output.transpose(1, 2).contiguous().view(
            batch_size, -1, self.num_heads * self.d_k)
        
        return self.W_o(attention_output)
```

**Key Algorithmic Insights:**
1. **Parallelization**: Unlike RNNs, all positions computed simultaneously
2. **Memory Efficiency**: Attention matrix can be computed in chunks
3. **Gradient Flow**: Direct paths between any two positions
                    """)
                    st.caption("Generated by Code Agent")
            
            with col3:
                st.markdown("""
                <div style='text-align: center; padding: 12px; background-color: #F9FAFB; border-radius: 8px; margin-bottom: 12px;'>
                    <h4 style='margin: 0; color: #4F46E5;'>Concept Agent</h4>
                    <p style='margin: 4px 0 0 0; font-size: 0.875rem; color: #6B7280;'>Ideas & Architecture</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("Show Concept Analysis", use_container_width=True, key="concept_btn"):
                    st.markdown("---")
                    st.markdown("#### Conceptual Analysis")
                    st.markdown("""
**Revolutionary Paradigm Shift: "Attention Is All You Need"**

**The Big Idea:**
Replace sequential processing (RNNs) and local processing (CNNs) with pure attention mechanisms that can directly model relationships between any two positions in a sequence.

**Core Architecture Concepts:**

**1. Encoder-Decoder Structure**
- **Encoder**: 6 identical layers, each with multi-head self-attention + feed-forward
- **Decoder**: 6 identical layers with masked self-attention + encoder-decoder attention + feed-forward

**2. Self-Attention Intuition**
Think of it as "each word asking every other word: how relevant are you to me?"
- Query: "What am I looking for?"
- Key: "What do I contain?"
- Value: "What information do I provide?"

**3. Multi-Head Attention Philosophy**
Different heads learn different types of relationships:
- Syntactic dependencies (subject-verb agreement)
- Semantic relationships (word meanings)
- Positional patterns (nearby words)

**4. Key Design Principles**
- **Parallelization**: Process entire sequences simultaneously
- **Long-range Dependencies**: Direct connections between distant positions  
- **Interpretability**: Attention weights show what the model focuses on
- **Scalability**: Architecture scales well with compute and data

**Impact on AI:**
This paper didn't just improve translation - it fundamentally changed how we think about sequence modeling, leading to GPT, BERT, and the entire transformer revolution in AI.

**Why It Worked:**
- Removed sequential bottleneck of RNNs
- Provided richer inductive biases than simple feedforward networks
- Enabled massive parallelization for training
- Created interpretable attention patterns
                    """)
                    st.caption("Generated by Concept Agent")
        
        else:
            # Live mode or other papers - show regular interface
            st.markdown("Select an agent to analyze your paper:")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("""
                <div style='text-align: center; padding: 12px; background-color: #F9FAFB; border-radius: 8px; margin-bottom: 12px;'>
                    <h4 style='margin: 0; color: #4F46E5;'>Math Agent</h4>
                    <p style='margin: 4px 0 0 0; font-size: 0.875rem; color: #6B7280;'>Equations & Proofs</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("Analyze Math", use_container_width=True, key="math_btn"):
                    with st.spinner("Analyzing mathematical content..."):
                        content = parser.full_text[:8000]
                        result = st.session_state.mode_handler.process_query(
                            paper['id'],
                            "Explain the mathematical concepts, equations, and proofs in this paper",
                            content,
                            query_type="math",
                            section=None
                        )
                        
                        st.markdown("---")
                        st.markdown("#### Mathematical Analysis")
                        st.markdown(result['response'])
                        st.caption(f"Generated by {result.get('agent', 'Math')} Agent")
            
            with col2:
                st.markdown("""
                <div style='text-align: center; padding: 12px; background-color: #F9FAFB; border-radius: 8px; margin-bottom: 12px;'>
                    <h4 style='margin: 0; color: #4F46E5;'>Code Agent</h4>
                    <p style='margin: 4px 0 0 0; font-size: 0.875rem; color: #6B7280;'>Algorithms & Implementation</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("Analyze Code", use_container_width=True, key="code_btn"):
                    with st.spinner("Analyzing algorithms..."):
                        content = parser.full_text[:8000]
                        result = st.session_state.mode_handler.process_query(
                            paper['id'],
                            "Explain the algorithms, pseudocode, and implementation details in this paper",
                            content,
                            query_type="code",
                            section=None
                        )
                        
                        st.markdown("---")
                        st.markdown("#### Algorithm Analysis")
                        st.markdown(result['response'])
                        st.caption(f"Generated by {result.get('agent', 'Code')} Agent")
            
            with col3:
                st.markdown("""
                <div style='text-align: center; padding: 12px; background-color: #F9FAFB; border-radius: 8px; margin-bottom: 12px;'>
                    <h4 style='margin: 0; color: #4F46E5;'>Concept Agent</h4>
                    <p style='margin: 4px 0 0 0; font-size: 0.875rem; color: #6B7280;'>Ideas & Architecture</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("Analyze Concepts", use_container_width=True, key="concept_btn"):
                    with st.spinner("Analyzing concepts..."):
                        content = parser.full_text[:8000]
                        result = st.session_state.mode_handler.process_query(
                            paper['id'],
                            "Explain the key concepts, architecture, and main ideas in this paper",
                            content,
                            query_type="concept",
                            section=None
                        )
                        
                        st.markdown("---")
                        st.markdown("#### Conceptual Analysis")
                        st.markdown(result['response'])
                        st.caption(f"Generated by {result.get('agent', 'Concept')} Agent")
    
    with tab2:
        st.markdown("### Interactive Chat")
        
        # Demo mode for Attention paper - show sample questions
        if st.session_state.mode_handler.mode == "demo" and paper['id'] == "attention":
            st.markdown("**Demo Mode**: Click on sample questions to see AI responses about 'Attention Is All You Need'")
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Sample questions
            demo_questions = [
                {
                    "question": "What is the main innovation of the Transformer?",
                    "answer": """The main innovation of the Transformer is **replacing recurrent and convolutional layers entirely with self-attention mechanisms**.

**Key breakthrough:** Instead of processing sequences step-by-step (like RNNs) or with local windows (like CNNs), the Transformer uses self-attention to directly model relationships between any two positions in a sequence, regardless of their distance.

**Why this matters:**
1. **Parallelization**: All positions can be computed simultaneously, dramatically speeding up training
2. **Long-range dependencies**: Direct connections between distant words (no information bottleneck)
3. **Interpretability**: Attention weights show exactly what the model is focusing on
4. **Scalability**: Architecture scales beautifully with more compute and data

This simple but powerful idea became the foundation for GPT, BERT, and virtually all modern large language models."""
                },
                {
                    "question": "How does self-attention work?",
                    "answer": """Self-attention works by allowing each position in a sequence to attend to all positions, including itself.

**The intuition:** Each word asks "Which other words are relevant to understanding me?"

**The mechanism:**
1. **Transform inputs**: Each input gets converted to Query (Q), Key (K), and Value (V) vectors
2. **Compute similarities**: Query of each position is compared with Keys of all positions (QK^T)
3. **Normalize**: Divide by √d_k to prevent gradients from vanishing
4. **Get probabilities**: Apply softmax to get attention weights
5. **Weighted sum**: Use weights to combine all Value vectors

**Formula:** `Attention(Q,K,V) = softmax(QK^T/√d_k)V`

**Example:** For the word "bank" in "I went to the bank to deposit money":
- It might attend strongly to "deposit" and "money" (financial context)
- Less to "went" and "to" (less relevant for meaning)
- This helps disambiguate "bank" as financial institution vs. river bank"""
                },
                {
                    "question": "Why use multiple attention heads?",
                    "answer": """Multiple attention heads allow the model to attend to different types of information simultaneously - like having multiple perspectives on the same data.

**The problem with single attention:**
One attention mechanism can only learn one way of relating words. But language has many types of relationships:
- Syntactic (subject-verb agreement)
- Semantic (word meanings)  
- Positional (nearby words)
- Discourse (topic flow)

**Multi-head solution:**
Each head learns different relationship patterns:
- **Head 1** might focus on syntactic dependencies ("The cats **are** sleeping" - linking subject to verb)
- **Head 2** might capture semantic relationships ("bank" attending to "money", "deposit")
- **Head 3** might learn positional patterns (attending to adjacent words)

**Implementation:**
- Run 8 attention heads in parallel (in the paper)
- Each head has its own Q, K, V projections
- Concatenate outputs and apply final linear layer
- Each head only sees d_model/num_heads dimensions

**Result:** The model can simultaneously understand syntax, semantics, and other linguistic patterns, making it much more powerful than single-head attention."""
                },
                {
                    "question": "What are the advantages over RNNs?",
                    "answer": """Transformers have several key advantages over RNNs:

**1. Parallelization**
- **RNNs**: Must process sequentially (word 1 → word 2 → word 3...)
- **Transformers**: Process entire sequence simultaneously
- **Impact**: Training is 10-100x faster on modern hardware

**2. Long-range dependencies**
- **RNNs**: Information must flow through many hidden states, causing gradient vanishing
- **Transformers**: Direct connections between any two positions
- **Impact**: Better understanding of long documents and complex relationships

**3. Interpretability**
- **RNNs**: Hidden states are opaque - hard to understand what the model learned
- **Transformers**: Attention weights show exactly which words the model focuses on
- **Impact**: Can visualize and debug model behavior

**4. Scalability**
- **RNNs**: Don't benefit much from larger models due to sequential bottleneck
- **Transformers**: Scale beautifully with more parameters and compute
- **Impact**: Enabled GPT-3, GPT-4, and other large language models

**5. Training stability**
- **RNNs**: Prone to exploding/vanishing gradients
- **Transformers**: More stable training with residual connections and layer norm
- **Impact**: Can train much deeper networks reliably

**Trade-off:** Transformers use O(n²) memory for sequence length n, while RNNs use O(n). But for typical lengths, the benefits far outweigh this cost."""
                },
                {
                    "question": "How does positional encoding work?",
                    "answer": """Positional encoding solves a fundamental problem: since attention is permutation-invariant, the model has no inherent sense of word order. "Cat chased dog" and "Dog chased cat" would look identical without position information.

**The solution:** Add positional information to input embeddings using sinusoidal functions.

**The formulas:**
```
PE(pos, 2i) = sin(pos / 10000^(2i/d_model))
PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))
```

**Why sinusoids?**
1. **Unique patterns**: Each position gets a unique combination of sine/cosine values
2. **Relative positions**: The model can learn to attend by relative distance
3. **Extrapolation**: Can handle sequences longer than seen during training
4. **Smooth**: Similar positions have similar encodings

**Intuition:**
- Think of it like a barcode for each position
- Position 1 gets one pattern, position 2 gets a slightly different pattern, etc.
- Different frequencies (controlled by i) create patterns at different scales
- Low frequencies change slowly (capture long-range patterns)
- High frequencies change quickly (capture local patterns)

**Alternative approaches:**
- Learned positional embeddings (used in BERT)
- Relative positional encodings (used in some variants)
- Rotary positional encoding (used in modern models like GPT-J)

The key insight: you need some way to inject order information, and sinusoids provide an elegant, parameter-free solution."""
                }
            ]
            
            # Display sample questions as buttons
            st.markdown("**Sample Questions:**")
            for i, qa in enumerate(demo_questions):
                if st.button(f"❓ {qa['question']}", key=f"demo_q_{i}", use_container_width=True):
                    # Add to chat history
                    st.session_state.chat_history.append({
                        "role": "user", 
                        "content": qa['question']
                    })
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": qa['answer']
                    })
                    st.rerun()
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("---")
        
        # Display chat history
        for msg in st.session_state.chat_history:
            with st.chat_message(msg['role']):
                st.markdown(msg['content'])
        
        # Chat input
        if st.session_state.mode_handler.mode == "demo" and paper['id'] == "attention":
            user_query = st.chat_input("Ask about the Transformer architecture (demo responses available for common questions)...")
        else:
            user_query = st.chat_input("Type your question here...")
        
        if user_query:
            # Add user message
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_query
            })
            
            # Get paper content
            content = parser.full_text[:8000]
            
            # Get response
            with st.spinner("Thinking..."):
                result = st.session_state.mode_handler.chat(
                    paper['id'],
                    user_query,
                    content,
                    history=st.session_state.chat_history[:-1],
                    section=None
                )
                
                # Add assistant response
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": result['response']
                })
                
                # Display the new message immediately
                with st.chat_message("assistant"):
                    st.markdown(result['response'])
    
    with tab3:
        st.markdown("### Quiz Generator")
        
        # Demo mode for Attention paper - show comprehensive quiz
        if st.session_state.mode_handler.mode == "demo" and paper['id'] == "attention":
            st.markdown("**Demo Mode**: Comprehensive quiz about 'Attention Is All You Need'")
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("Show Quiz Questions", type="primary", use_container_width=True):
                st.markdown("---")
                st.markdown("#### Study Questions: Attention Is All You Need")
                
                st.markdown("""
**Question 1: Conceptual Understanding**
What fundamental limitation of RNNs does the Transformer address, and how?

<details>
<summary>Click to see answer</summary>

**Answer:**
RNNs process sequences sequentially, creating two problems: (1) prevents parallelization during training, and (2) makes learning long-range dependencies difficult because information must propagate through many sequential steps.

The Transformer solves this by using self-attention to directly connect any two positions in the sequence, regardless of distance. All positions are processed in parallel, enabling both faster training and better modeling of long-range relationships.

**Why this matters:** Understanding this motivation is key to grasping why Transformers revolutionized NLP.
</details>

---

**Question 2: Mathematical Details**
Why is the dot product scaled by √d_k in the attention formula?

<details>
<summary>Click to see answer</summary>

**Answer:**
As the dimension d_k grows larger, the dot products grow in magnitude, pushing the softmax function into regions with extremely small gradients, making training difficult.

Dividing by √d_k counteracts this effect. The scaling factor is chosen because if q and k are vectors with mean 0 and variance 1, their dot product has mean 0 and variance d_k. Dividing by √d_k normalizes the variance back to 1.

**Why this matters:** Without this scaling, the model would be difficult to train, especially with larger embedding dimensions.
</details>

---

**Question 3: Architecture Design**
What is the purpose of using multiple attention heads instead of a single attention mechanism?

<details>
<summary>Click to see answer</summary>

**Answer:**
Multi-head attention allows the model to jointly attend to information from different representation subspaces at different positions. Each head can learn to focus on different types of relationships:
- One head might focus on syntactic dependencies
- Another on semantic relationships  
- Another on positional patterns

The outputs are concatenated and projected, combining insights from all heads. This is more powerful than single-head attention, which would be forced to learn a single way of attending.

**Why this matters:** Multi-head attention is what makes Transformers so powerful - multiple perspectives on the data simultaneously.
</details>

---

**Question 4: Critical Thinking**
What are potential limitations of the Transformer architecture?

<details>
<summary>Click to see answer</summary>

**Answer:**
Several limitations:

1. **Quadratic complexity**: Self-attention has O(n²) complexity in sequence length, making very long sequences expensive
2. **Position encoding**: The sinusoidal encoding is fixed; the model must learn to use it effectively
3. **No built-in sequential bias**: Unlike RNNs, doesn't have inherent sequential inductive bias
4. **Memory requirements**: Attending to full sequence requires storing large attention matrices

**Why this matters:** Understanding limitations guides when to use Transformers vs other architectures and motivates improvements like efficient attention variants.
</details>

---

**Question 5: Practical Application**
How would you adapt the Transformer architecture for computer vision tasks?

<details>
<summary>Click to see answer</summary>

**Answer:**
For images, you'd need to:

1. **Patch embedding**: Divide image into patches (e.g., 16x16), flatten and embed them
2. **2D positional encoding**: Extend position encodings to 2D space (x,y coordinates)  
3. **Attention patterns**: Could use full attention or restricted patterns (local windows, axial attention)
4. **Output adaptation**: Use [CLS] token for classification or adapt for segmentation

This is essentially what Vision Transformer (ViT) does! The key insight: treat image patches like tokens in a sequence.

**Why this matters:** Shows that attention-based architectures are domain-agnostic and can replace convolutions.
</details>

---

**Question 6: Implementation Details**
Explain the role of residual connections and layer normalization in the Transformer.

<details>
<summary>Click to see answer</summary>

**Answer:**
**Residual connections** (skip connections) help with:
- **Gradient flow**: Provide direct paths for gradients to flow backward
- **Training stability**: Prevent vanishing gradients in deep networks
- **Identity mapping**: Allow layers to learn modifications to the input rather than complete transformations

**Layer normalization** helps with:
- **Training stability**: Normalizes inputs to each layer
- **Faster convergence**: Reduces internal covariate shift
- **Gradient flow**: Keeps gradients in a reasonable range

**Together:** They enable training much deeper networks (6+ layers) reliably, which is crucial for the Transformer's performance.
</details>

---

**Bonus Question: Historical Impact**
Why did this paper become so influential in AI research?

<details>
<summary>Click to see answer</summary>

**Answer:**
The paper was influential because it:

1. **Simplified architecture**: Removed complex recurrent/convolutional components
2. **Enabled scaling**: Architecture scales beautifully with compute and data
3. **Improved performance**: Achieved state-of-the-art results on translation
4. **Faster training**: Parallelization made training much more efficient
5. **Broad applicability**: Attention mechanism works across many domains

**Long-term impact:** This paper laid the foundation for GPT, BERT, and the entire modern AI revolution. The "attention is all you need" insight fundamentally changed how we approach sequence modeling and led to today's large language models.
</details>
                """, unsafe_allow_html=True)
                
                st.caption("Generated by Quiz Agent")
        
        else:
            # Live mode or other papers - show regular interface
            st.markdown("Generate study questions to test your understanding:")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("Generate Quiz Questions", type="primary", use_container_width=True):
                    with st.spinner("Generating study questions..."):
                        content = parser.full_text[:8000]
                        
                        result = st.session_state.mode_handler.process_query(
                            paper['id'],
                            "Generate quiz questions about this research paper",
                            content,
                            query_type="quiz",
                            section=None
                        )
                        
                        st.markdown("---")
                        st.markdown("#### Study Questions")
                        st.markdown(result['response'])
                        st.caption("Generated by Quiz Agent")

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; padding: 24px; background-color: #F9FAFB; border-radius: 12px; margin-top: 48px;'>
    <p style='color: #6B7280; margin: 0; font-size: 0.875rem;'>
        Built with ❤️ using Streamlit & Google Gemini AI
    </p>
    <p style='color: #9CA3AF; margin: 8px 0 0 0; font-size: 0.75rem;'>
        Google's 5-Day AI Agents Intensive - Capstone Project
    </p>
</div>
""", unsafe_allow_html=True)