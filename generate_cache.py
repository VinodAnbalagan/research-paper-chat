#!/usr/bin/env python3
"""
Cache Generator for Research Paper Chat
Generates cached responses for sample papers to enable Demo mode
"""

import os
import json
import yaml
from dotenv import load_dotenv
from tools.pdf_parser import PaperParser
from backend.manager import ManagerAgent
from backend.agents.quiz_agent import QuizAgent
from backend.agents.chat_agent import ChatAgent

# Load environment
load_dotenv()

def generate_cache_for_paper(paper_config):
    """Generate comprehensive cache for a paper"""
    print(f"\n{'='*60}")
    print(f"Generating cache for: {paper_config['title']}")
    print(f"{'='*60}")
    
    paper_path = f"data/sample_papers/{paper_config['file']}"
    
    if not os.path.exists(paper_path):
        print(f"[FAIL] Paper not found: {paper_path}")
        return None
    
    # Parse paper
    print("[INFO] Parsing PDF...")
    parser = PaperParser(paper_path)
    parser.extract_sections()
    
    cache = {}
    manager = ManagerAgent()
    quiz_agent = QuizAgent()
    chat_agent = ChatAgent()
    
    # Generate explanations for each section
    print("\n[INFO] Generating section explanations...")
    for section_name, section_content in parser.sections.items():
        print(f"  Processing: {section_name}")
        
        # Math explanation
        try:
            result = manager.process_query(
                f"Explain the mathematical concepts in the {section_name} section",
                section_content,
                section=section_name,
                agent_type="math"
            )
            cache[f"explain_{section_name}_math"] = result['response']
            print(f"    [PASS] Math explanation")
        except Exception as e:
            print(f"    [WARN] Math explanation failed: {e}")
        
        # Code explanation
        try:
            result = manager.process_query(
                f"Explain the algorithms and implementation in the {section_name} section",
                section_content,
                section=section_name,
                agent_type="code"
            )
            cache[f"explain_{section_name}_code"] = result['response']
            print(f"    [PASS] Code explanation")
        except Exception as e:
            print(f"    [WARN] Code explanation failed: {e}")
        
        # Concept explanation
        try:
            result = manager.process_query(
                f"Explain the key concepts in the {section_name} section",
                section_content,
                section=section_name,
                agent_type="concept"
            )
            cache[f"explain_{section_name}_concept"] = result['response']
            print(f"    [PASS] Concept explanation")
        except Exception as e:
            print(f"    [WARN] Concept explanation failed: {e}")
    
    # Generate quizzes
    print("\n[INFO] Generating quizzes...")
    
    # General quiz
    try:
        response = quiz_agent.process(
            "Generate quiz questions",
            parser.full_text[:4000],
            section=None
        )
        cache["quiz_general"] = response
        print("  [PASS] General quiz")
    except Exception as e:
        print(f"  [WARN] General quiz failed: {e}")
    
    # Section-specific quizzes
    for section_name, section_content in parser.sections.items():
        try:
            response = quiz_agent.process(
                f"Generate quiz questions for {section_name}",
                section_content,
                section=section_name
            )
            cache[f"quiz_{section_name}"] = response
            print(f"  [PASS] Quiz for {section_name}")
        except Exception as e:
            print(f"  [WARN] Quiz for {section_name} failed: {e}")
    
    # Generate common chat responses
    print("\n[INFO] Generating chat responses...")
    common_questions = [
        "What is the main contribution of this paper?",
        "What are the key innovations?",
        "What are the limitations?",
        "How does this compare to previous work?",
        "What are the practical applications?"
    ]
    
    for question in common_questions:
        try:
            response = chat_agent.chat(
                question,
                parser.full_text[:3000],
                history=None,
                section=None
            )
            key = f"chat_{question.lower().replace(' ', '_').replace('?', '')}"
            cache[key] = response
            print(f"  [PASS] {question}")
        except Exception as e:
            print(f"  [WARN] {question} failed: {e}")
    
    # Add general chat response
    cache["chat_general"] = f"I'm ready to answer questions about '{paper_config['title']}'. Feel free to ask about any aspect - the architecture, the math, the training process, or how it compares to other approaches!"
    
    return cache

def save_cache(paper_id, cache_data):
    """Save cache to file"""
    cache_dir = "data/cached_responses"
    os.makedirs(cache_dir, exist_ok=True)
    
    cache_path = os.path.join(cache_dir, f"{paper_id}.json")
    
    with open(cache_path, 'w') as f:
        json.dump(cache_data, f, indent=2)
    
    print(f"\n[INFO] Cache saved to: {cache_path}")
    print(f"[INFO] Total cached responses: {len(cache_data)}")

def main():
    """Main function"""
    print("=" * 60)
    print("Research Paper Chat - Cache Generator")
    print("=" * 60)
    
    # Check API key
    if not os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY") == "your-api-key-here":
        print("\n[FAIL] Error: GOOGLE_API_KEY not set in .env file")
        print("[INFO] Get your key from: https://aistudio.google.com/app/apikey")
        return 1
    
    # Load config
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    papers = config['sample_papers']
    
    print(f"\nFound {len(papers)} paper(s) in config")
    print("\n[WARN] WARNING: This will make many API calls!")
    print("Estimated: ~20-30 calls per paper")
    print("Free tier limit: 15 requests/minute, 1500/day")
    
    response = input("\nContinue? (yes/no): ")
    if response.lower() != 'yes':
        print("Cancelled.")
        return 0
    
    # Generate cache for each paper
    for paper in papers:
        try:
            cache = generate_cache_for_paper(paper)
            if cache:
                save_cache(paper['id'], cache)
                print(f"[PASS] Successfully generated cache for {paper['title']}")
        except Exception as e:
            print(f"[FAIL] Error generating cache for {paper['title']}: {e}")
    
    print("\n" + "=" * 60)
    print("[PASS] Cache generation complete!")
    print("[INFO] You can now use Demo mode with these papers")
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
