#!/usr/bin/env python3
"""
Generate cache for a single paper
Usage: python generate_single_cache.py <paper_id>
Example: python generate_single_cache.py dqn
"""

import sys
import os
import json
import yaml
from dotenv import load_dotenv
from tools.pdf_parser import PaperParser
from backend.manager import ManagerAgent
from backend.agents.quiz_agent import QuizAgent
from backend.agents.chat_agent import ChatAgent

load_dotenv()

def generate_cache_for_paper(paper_config):
    """Generate comprehensive cache for a paper"""
    print(f"\nGenerating cache for: {paper_config['title']}")
    print("=" * 60)
    
    paper_path = f"data/sample_papers/{paper_config['file']}"
    
    if not os.path.exists(paper_path):
        print(f"[FAIL] Paper not found: {paper_path}")
        return None
    
    print("[INFO] Parsing PDF...")
    parser = PaperParser(paper_path)
    parser.extract_sections()
    
    cache = {}
    manager = ManagerAgent()
    quiz_agent = QuizAgent()
    
    print(f"\n[INFO] Found {len(parser.sections)} sections")
    print("[INFO] Generating explanations (this will take a few minutes)...")
    
    # Generate explanations for each section
    for i, (section_name, section_content) in enumerate(parser.sections.items(), 1):
        print(f"\n[{i}/{len(parser.sections)}] Processing: {section_name}")
        
        # Math explanation
        try:
            result = manager.process_query(
                f"Explain the mathematical concepts in the {section_name} section",
                section_content,
                section=section_name,
                agent_type="math"
            )
            cache[f"explain_{section_name}_math"] = result['response']
            print(f"  [PASS] Math explanation")
        except Exception as e:
            print(f"  [WARN] Math explanation failed: {str(e)[:100]}")
        
        # Code explanation
        try:
            result = manager.process_query(
                f"Explain the algorithms in the {section_name} section",
                section_content,
                section=section_name,
                agent_type="code"
            )
            cache[f"explain_{section_name}_code"] = result['response']
            print(f"  [PASS] Code explanation")
        except Exception as e:
            print(f"  [WARN] Code explanation failed: {str(e)[:100]}")
        
        # Concept explanation
        try:
            result = manager.process_query(
                f"Explain the key concepts in the {section_name} section",
                section_content,
                section=section_name,
                agent_type="concept"
            )
            cache[f"explain_{section_name}_concept"] = result['response']
            print(f"  [PASS] Concept explanation")
        except Exception as e:
            print(f"  [WARN] Concept explanation failed: {str(e)[:100]}")
    
    # Generate quizzes
    print("\n[INFO] Generating quizzes...")
    
    try:
        response = quiz_agent.process(
            "Generate quiz questions",
            parser.full_text[:4000],
            section=None
        )
        cache["quiz_general"] = response
        print("  [PASS] General quiz")
    except Exception as e:
        print(f"  [WARN] General quiz failed: {str(e)[:100]}")
    
    # Add general chat response
    cache["chat_general"] = f"I'm ready to answer questions about '{paper_config['title']}'. Feel free to ask about any aspect!"
    
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
    if len(sys.argv) < 2:
        print("Usage: python generate_single_cache.py <paper_id>")
        print("\nAvailable paper IDs:")
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
        for paper in config['sample_papers']:
            print(f"  - {paper['id']}: {paper['title']}")
        return 1
    
    paper_id = sys.argv[1]
    
    # Check API key
    if not os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY") == "your-api-key-here":
        print("[FAIL] Error: GOOGLE_API_KEY not set in .env file")
        return 1
    
    # Load config
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    # Find paper
    paper = None
    for p in config['sample_papers']:
        if p['id'] == paper_id:
            paper = p
            break
    
    if not paper:
        print(f"[FAIL] Paper '{paper_id}' not found in config")
        return 1
    
    print("=" * 60)
    print("Research Paper Chat - Single Paper Cache Generator")
    print("=" * 60)
    print(f"\nPaper: {paper['title']}")
    print(f"Estimated API calls: ~20-25")
    print(f"Estimated time: 5-10 minutes")
    
    response = input("\nContinue? (yes/no): ")
    if response.lower() != 'yes':
        print("Cancelled.")
        return 0
    
    try:
        cache = generate_cache_for_paper(paper)
        if cache:
            save_cache(paper['id'], cache)
            print(f"\n[PASS] Successfully generated cache for {paper['title']}")
            print("\n[INFO] You can now use this paper in Demo mode!")
    except Exception as e:
        print(f"\n[FAIL] Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
