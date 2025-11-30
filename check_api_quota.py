#!/usr/bin/env python3
"""
Check Google AI Studio API quota status
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

def check_quota():
    """Check if API key is working and has quota"""
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key or api_key == "your-api-key-here":
        print("[FAIL] No API key configured")
        return False
    
    print(f"[INFO] API Key: {api_key[:20]}...")
    
    try:
        genai.configure(api_key=api_key)
        
        # Try a minimal request
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(
            "Say 'OK'",
            generation_config=genai.GenerationConfig(
                max_output_tokens=10,
                temperature=0
            )
        )
        
        print("[PASS] API key is valid and has quota available")
        print(f"[INFO] Response: {response.text}")
        return True
        
    except Exception as e:
        error_str = str(e)
        
        if "429" in error_str or "quota" in error_str.lower():
            print("[FAIL] Quota exceeded")
            print("[INFO] You've hit your rate limit or daily quota")
            
            if "retry in" in error_str.lower():
                # Extract wait time
                import re
                match = re.search(r'retry in (\d+)', error_str)
                if match:
                    seconds = int(match.group(1))
                    minutes = seconds // 60
                    print(f"[INFO] Rate limit: Wait {minutes} minutes {seconds % 60} seconds")
            
            print("\n[INFO] Possible causes:")
            print("  1. Hit per-minute rate limit (15 requests/min)")
            print("  2. Hit daily quota (1500 requests/day)")
            print("  3. Model-specific quota exhausted")
            
            print("\n[INFO] Solutions:")
            print("  1. Wait for rate limit to reset")
            print("  2. Use Demo mode (no API calls)")
            print("  3. Check usage: https://ai.dev/usage?tab=rate-limit")
            
        elif "401" in error_str or "invalid" in error_str.lower():
            print("[FAIL] Invalid API key")
            print("[INFO] Get a new key: https://aistudio.google.com/app/apikey")
        else:
            print(f"[FAIL] Error: {error_str[:200]}")
        
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Google AI Studio API Quota Checker")
    print("=" * 60)
    print()
    
    check_quota()
    
    print()
    print("=" * 60)
