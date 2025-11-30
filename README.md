# 📚 Research Paper Chat

> AI-Powered Research Paper Analysis with Specialized Agents

A modern, intelligent system that helps researchers understand complex papers through specialized AI agents. Built with Streamlit and Google Gemini AI.

**Built for Google's 5-Day AI Agents Intensive - Capstone Project**

Try the live demo  [![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://vinodanbalagan-research-paper-chat-app-x3nxo4.streamlit.app/)

[![Watch the Live Demo](https://img.shields.io/badge/Watch%20Demo-red?logo=youtube&style=flat&logoColor=white)](https://youtu.be/vmrn7zhfwQY)

![Modern UI](https://img.shields.io/badge/UI-Modern%20%26%20Minimalistic-blue)
![AI Powered](https://img.shields.io/badge/AI-Google%20Gemini-purple)
![License](https://img.shields.io/badge/license-MIT-green)

## Problem Statement

Research papers are dense, math-heavy, and time-consuming to study. Reading, understanding equations, grasping algorithms, and retaining knowledge across multiple papers is challenging. This system reduces study time through specialized AI agents that explain math, code, and concepts interactively.

## Key Features

### Specialized Agents

- **Math Agent**: Explains equations, proofs, and mathematical intuition
- **Code Agent**: Breaks down algorithms and implementation details
- **Concept Agent**: Explains high-level ideas and architecture
- **Quiz Agent**: Generates study questions to test understanding
- **Chat Agent**: Interactive Q&A about specific sections

### Real-Time AI Analysis

- Powered by Google Gemini 2.5 Flash
- Custom PDF upload support
- Adaptive routing to specialized agents
- Intelligent question answering

## Architecture

```
Streamlit Frontend
       ↓
  Manager Agent
       ↓
  ┌────┼────┐
Math Code Concept
Agent Agent Agent
  └────┼────┘
   Quiz/Chat
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Google AI Studio API key (free!)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/research-paper-chat.git
cd research-paper-chat

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Mac/Linux
# or: .venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
```

### Get Your Free API Key

1. Go to Google AI Studio
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key
5. Open `.env` and replace `your-api-key-here` with your actual key

**Free Tier Limits:**

- 15 requests per minute
- 1,500 requests per day
- No credit card required!

### Verify Setup

```bash
# Run the setup checker
python check_setup.py
```

This will verify all dependencies and files are properly configured.

### Run Locally

```bash
streamlit run app.py
```

Access at `http://localhost:8501`

### First Time Usage

1. **Start with Demo Mode** (default) - Uses cached responses for "Attention Is All You Need" paper
2. **Try Live Mode** - Switch in sidebar to use real-time AI agents (requires API key)
3. **Upload Your Own Papers** - Works with any research paper PDF!

## Usage Guide

### Demo Mode (Recommended for First Use)

1. Select **Demo Mode** in sidebar
2. Choose a sample paper
3. Click "Load Paper"
4. Explore sections, generate quizzes, or chat
5. Get instant cached responses

### Live Mode (Requires API Key)

1. Select **Live Mode** in sidebar
2. Upload custom PDF or use sample paper
3. Ask any question - Manager routes to appropriate agent
4. Get real-time AI-generated responses

### Example Queries

**Math Questions:**

- "Explain the attention formula"
- "Why divide by √dk?"
- "How does backpropagation work here?"

**Code Questions:**

- "Explain the training algorithm"
- "What's the time complexity?"
- "How is this implemented?"

**Concept Questions:**

- "What's the main innovation?"
- "How does this compare to RNNs?"
- "Why does this architecture work?"

## Project Structure

```
research-paper-chat/
├── app.py                      # Streamlit application
├── config.yaml                 # Configuration
├── requirements.txt            # Dependencies
├── .env                        # Environment variables (create from .env.example)
│
├── backend/
│   ├── manager.py             # Manager agent (orchestrator)
│   ├── mode_handler.py        # Demo/Live mode switching
│   └── agents/
│       ├── math_agent.py      # Math specialist
│       ├── code_agent.py      # Code/algorithm specialist
│       ├── concept_agent.py   # Concept specialist
│       ├── quiz_agent.py      # Quiz generator
│       └── chat_agent.py      # Interactive chat
│
├── tools/
│   └── pdf_parser.py          # PDF text extraction
│
├── utils/
│   ├── vertex_client.py       # Gemini API wrapper
│   └── response_cache.py      # Cache management
│
└── data/
    ├── sample_papers/         # Sample PDFs
    └── cached_responses/      # Pre-computed answers
```

## Technical Details

### Agent Routing Logic

The Manager Agent analyzes each query and routes to specialists:

1. **Pattern Matching**: Checks for math/code keywords
2. **Content Analysis**: Examines paper content
3. **LLM Decision**: Uses Gemini for ambiguous cases
4. **Agent Invocation**: Calls appropriate specialist

### Response Caching Strategy

Demo mode uses pre-computed responses:

- Stored as JSON in `data/cached_responses/`
- Keyed by paper_id + query_type + section
- Instant responses (no API calls)
- Fallback to Live mode if no cache hit

## Evaluation

### Capstone Requirements

**Multi-agent system**: Manager + 5 specialized agents  
 **Custom tools**: PDF parser, section extractor  
 **Sessions & Memory**: Chat history management  
 **Context engineering**: Section-focused content  
 **Observability**: Logging throughout  
 **Agent deployment**: Streamlit Cloud ready

### Performance Metrics

- **Demo Mode**: <100ms response time
- **Live Mode**: 2-5s per query
- **Accuracy**: High (validated against papers)
- **User Satisfaction**: Tested with 10+ papers

## 🚀 Deploying to Streamlit Cloud

### Step 1: Prepare Your Repository

1. Push your code to GitHub
2. Make sure `.env` is in `.gitignore` (it already is!)
3. Ensure `requirements.txt` is up to date

### Step 2: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select your repository and branch
5. Set main file path: `app.py`
6. Click "Deploy"

### Step 3: Configure Secrets

1. In your app dashboard, click "⚙️ Settings"
2. Go to "Secrets" section
3. Add your secrets:

```toml
GOOGLE_API_KEY = "your-actual-api-key-here"
APP_MODE = "demo"
```

4. Save and your app will restart

### Step 4: Test Your Deployment

- Demo mode should work immediately (uses cached responses)
- Live mode will work once API key is configured
- Share your app URL with others!

### Cost Management

**To preserve your free API credits:**

1. Keep `APP_MODE = "demo"` in secrets
2. Generate comprehensive caches before deployment
3. Only enable Live mode when needed
4. Monitor usage at [Google AI Studio](https://aistudio.google.com)

**When you want to stop API usage:**

1. Set `APP_MODE = "demo"` in Streamlit secrets
2. App will only use cached responses
3. Demo will work forever with no API costs!

## 🎬 Demo Video

Watch the full demo: [YouTube Link]()

## 📝 Blog Post

Read the full technical writeup: [Gradient Ascent on Substack](https://substack.com/@vinodanbalagan)

## 🔮 Future Enhancements

- [ ] Equation visualization with matplotlib
- [ ] Visual concept map generation
- [ ] Figure/table extraction and analysis
- [ ] Citation graph across papers
- [ ] Export notes to Markdown

## 🙏 Acknowledgments

Built for **Google's 5-Day Generative AI Intensive**.

Special thanks to:

- Google X kaggle Team

## 📄 License

MIT License - see LICENSE file

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repo
2. Create a feature branch
3. Submit a pull request

## 📧 Contact

**Vinod Anbalagan**

- Substack: [Gradient Ascent](https://substack.com/@vinodanbalagan)

---

**Star ⭐ this repo if you find it helpful!**
