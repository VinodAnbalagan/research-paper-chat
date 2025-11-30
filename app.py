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
    
    # Set to Live mode only
    if st.session_state.mode_handler.mode != "live":
        st.session_state.mode_handler.set_mode("live")
    
    # Paper upload section
    st.markdown("#### 📄 Upload Paper")
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help="Upload any research paper in PDF format",
        label_visibility="collapsed"
    )
    
    if uploaded_file:
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
    
    # Current paper info
    if st.session_state.current_paper:
        st.markdown("#### 📖 Current Paper")
        st.info(st.session_state.current_paper['title'])
    
    st.markdown("---")
    
    # API status
    st.markdown("#### ⚡ Status")
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key and api_key != "your-api-key-here":
        st.success("✓ API Connected")
        st.caption("Powered by Google Gemini AI")
    else:
        st.error("✗ API key not configured")
        st.caption("[Get your free key](https://aistudio.google.com/app/apikey)")
    
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
    
    # Feature cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 24px; border-radius: 12px; color: white; text-align: center;'>
            <h3 style='color: white; margin: 0;'>🤖 AI Agents</h3>
            <p style='margin: 8px 0 0 0; opacity: 0.9;'>Specialized agents for Math, Code, and Concepts</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 24px; border-radius: 12px; color: white; text-align: center;'>
            <h3 style='color: white; margin: 0;'>💬 Smart Chat</h3>
            <p style='margin: 8px 0 0 0; opacity: 0.9;'>Interactive Q&A with context awareness</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 24px; border-radius: 12px; color: white; text-align: center;'>
            <h3 style='color: white; margin: 0;'>❓ Quiz Gen</h3>
            <p style='margin: 8px 0 0 0; opacity: 0.9;'>Auto-generate study questions</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # How it works
    st.markdown("### 🚀 How It Works")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **1. Upload**  
        Drop your research paper PDF in the sidebar
        """)
    
    with col2:
        st.markdown("""
        **2. Analyze**  
        Choose an AI agent or start chatting
        """)
    
    with col3:
        st.markdown("""
        **3. Learn**  
        Get instant explanations and insights
        """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Call to action
    st.info("👈 **Get Started:** Upload a PDF from the sidebar to begin!")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Powered by
    st.markdown("""
    <div style='text-align: center; padding: 24px; background-color: #F9FAFB; border-radius: 12px;'>
        <p style='color: #6B7280; margin: 0;'>Powered by</p>
        <h3 style='color: #4F46E5; margin: 8px 0 0 0;'>Google Gemini AI</h3>
    </div>
    """, unsafe_allow_html=True)
    


else:
    # Paper is loaded
    paper = st.session_state.current_paper
    parser = st.session_state.paper_parser
    
    st.title(f"📄 {paper['title']}")
    
    # Extract sections if not already done
    if not parser.sections:
        with st.spinner("Extracting paper sections..."):
            parser.extract_sections()
    
    # Tabs for different actions
    tab1, tab2, tab3 = st.tabs(["Explain", "Chat", "Quiz"])
    
    with tab1:
        st.markdown("### 🤖 AI Agents")
        st.markdown("Select an agent to analyze your paper:")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style='text-align: center; padding: 12px; background-color: #F9FAFB; border-radius: 8px; margin-bottom: 12px;'>
                <h4 style='margin: 0; color: #4F46E5;'>🧮 Math Agent</h4>
                <p style='margin: 4px 0 0 0; font-size: 0.875rem; color: #6B7280;'>Equations & Proofs</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Analyze Math", use_container_width=True, key="math_btn"):
                with st.spinner("🔍 Analyzing mathematical content..."):
                    content = parser.full_text[:8000]
                    result = st.session_state.mode_handler.process_query(
                        paper['id'],
                        "Explain the mathematical concepts, equations, and proofs in this paper",
                        content,
                        query_type="math",
                        section=None
                    )
                    
                    st.markdown("---")
                    st.markdown("#### 📊 Mathematical Analysis")
                    st.markdown(result['response'])
                    st.caption(f"✓ Generated by {result.get('agent', 'Math')} Agent")
        
        with col2:
            st.markdown("""
            <div style='text-align: center; padding: 12px; background-color: #F9FAFB; border-radius: 8px; margin-bottom: 12px;'>
                <h4 style='margin: 0; color: #4F46E5;'>💻 Code Agent</h4>
                <p style='margin: 4px 0 0 0; font-size: 0.875rem; color: #6B7280;'>Algorithms & Implementation</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Analyze Code", use_container_width=True, key="code_btn"):
                with st.spinner("🔍 Analyzing algorithms..."):
                    content = parser.full_text[:8000]
                    result = st.session_state.mode_handler.process_query(
                        paper['id'],
                        "Explain the algorithms, pseudocode, and implementation details in this paper",
                        content,
                        query_type="code",
                        section=None
                    )
                    
                    st.markdown("---")
                    st.markdown("#### 💡 Algorithm Analysis")
                    st.markdown(result['response'])
                    st.caption(f"✓ Generated by {result.get('agent', 'Code')} Agent")
        
        with col3:
            st.markdown("""
            <div style='text-align: center; padding: 12px; background-color: #F9FAFB; border-radius: 8px; margin-bottom: 12px;'>
                <h4 style='margin: 0; color: #4F46E5;'>🎯 Concept Agent</h4>
                <p style='margin: 4px 0 0 0; font-size: 0.875rem; color: #6B7280;'>Ideas & Architecture</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Analyze Concepts", use_container_width=True, key="concept_btn"):
                with st.spinner("🔍 Analyzing concepts..."):
                    content = parser.full_text[:8000]
                    result = st.session_state.mode_handler.process_query(
                        paper['id'],
                        "Explain the key concepts, architecture, and main ideas in this paper",
                        content,
                        query_type="concept",
                        section=None
                    )
                    
                    st.markdown("---")
                    st.markdown("#### 🌟 Conceptual Analysis")
                    st.markdown(result['response'])
                    st.caption(f"✓ Generated by {result.get('agent', 'Concept')} Agent")
    
    with tab2:
        st.markdown("### 💬 Interactive Chat")
        st.markdown("Ask any questions about the paper:")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Display chat history
        for msg in st.session_state.chat_history:
            with st.chat_message(msg['role']):
                st.markdown(msg['content'])
        
        # Chat input
        user_query = st.chat_input("💭 Type your question here...")
        
        if user_query:
            # Add user message
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_query
            })
            
            # Get paper content
            content = parser.full_text[:8000]
            
            # Get response
            with st.spinner("🤔 Thinking..."):
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
        st.markdown("### ❓ Quiz Generator")
        st.markdown("Generate study questions to test your understanding:")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🎯 Generate Quiz Questions", type="primary", use_container_width=True):
                with st.spinner("✨ Generating study questions..."):
                    content = parser.full_text[:8000]
                    
                    result = st.session_state.mode_handler.process_query(
                        paper['id'],
                        "Generate quiz questions about this research paper",
                        content,
                        query_type="quiz",
                        section=None
                    )
                    
                    st.markdown("---")
                    st.markdown("#### 📝 Study Questions")
                    st.markdown(result['response'])
                    st.caption("✓ Generated by Quiz Agent")

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