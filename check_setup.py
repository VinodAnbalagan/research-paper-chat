#!/usr/bin/env python3
"""
Setup checker for Research Paper Chat
Verifies that all dependencies and files are properly configured
"""

import os
import sys
from pathlib import Path

def check_env_file():
    """Check if .env file exists and has API key"""
    print("Checking environment configuration...")
    
    if not os.path.exists(".env"):
        print("  [FAIL] .env file not found")
        print("  [INFO] Run: cp .env.example .env")
        print("  [INFO] Then edit .env and add your Google API key")
        return False
    
    with open(".env", "r") as f:
        content = f.read()
        # Check if API key line exists and is not the placeholder
        for line in content.split('\n'):
            if line.startswith('GOOGLE_API_KEY='):
                key_value = line.split('=', 1)[1].strip()
                if key_value == "your-api-key-here" or key_value == "":
                    print("  [WARN] .env file exists but API key not set")
                    print("  [INFO] Get your key from: https://aistudio.google.com/app/apikey")
                    print("  [INFO] Then update GOOGLE_API_KEY in .env")
                    return False
                break
    
    print("  [PASS] .env file configured")
    return True

def check_directories():
    """Check if required directories exist"""
    print("\nChecking directories...")
    
    dirs = [
        "data/sample_papers",
        "data/cached_responses",
        "backend/agents",
        "tools",
        "utils"
    ]
    
    all_exist = True
    for dir_path in dirs:
        if os.path.exists(dir_path):
            print(f"  [PASS] {dir_path}")
        else:
            print(f"  [FAIL] {dir_path} not found")
            all_exist = False
    
    return all_exist

def check_sample_papers():
    """Check which sample papers are available"""
    print("\nChecking sample papers...")
    
    papers = [
        "attention_is_all_you_need.pdf",
        "dqn_atari.pdf",
        "alexnet.pdf"
    ]
    
    found = 0
    for paper in papers:
        path = f"data/sample_papers/{paper}"
        if os.path.exists(path):
            print(f"  [PASS] {paper}")
            found += 1
        else:
            print(f"  [FAIL] {paper} not found")
    
    print(f"\n  [INFO] {found}/{len(papers)} sample papers available")
    return found > 0

def check_cache_files():
    """Check which cache files exist"""
    print("\nChecking cache files...")
    
    cache_dir = "data/cached_responses"
    if not os.path.exists(cache_dir):
        print("  [FAIL] Cache directory not found")
        return False
    
    cache_files = [f for f in os.listdir(cache_dir) if f.endswith('.json')]
    
    if cache_files:
        print(f"  [PASS] Found {len(cache_files)} cache file(s):")
        for cache_file in cache_files:
            print(f"     - {cache_file}")
        return True
    else:
        print("  [WARN] No cache files found (Demo mode will have limited functionality)")
        return False

def check_dependencies():
    """Check if key dependencies are installed"""
    print("\nChecking Python dependencies...")
    
    required = [
        "streamlit",
        "google.generativeai",
        "pdfplumber",
        "python-dotenv"
    ]
    
    all_installed = True
    for package in required:
        try:
            # Handle special cases for package names
            if package == "python-dotenv":
                __import__("dotenv")
            else:
                __import__(package.replace("-", "_"))
            print(f"  [PASS] {package}")
        except ImportError:
            print(f"  [FAIL] {package} not installed")
            all_installed = False
    
    if not all_installed:
        print("\n  [INFO] Run: pip install -r requirements.txt")
    
    return all_installed

def main():
    """Run all checks"""
    print("=" * 60)
    print("Research Paper Chat - Setup Checker")
    print("=" * 60)
    
    checks = {
        "Dependencies": check_dependencies(),
        "Directories": check_directories(),
        "Environment": check_env_file(),
        "Sample Papers": check_sample_papers(),
        "Cache Files": check_cache_files()
    }
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    for check_name, passed in checks.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {check_name}")
    
    all_passed = all(checks.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("All checks passed! You're ready to run the app.")
        print("\n[INFO] Run: streamlit run app.py")
    else:
        print("Some checks failed. Please fix the issues above.")
        print("\n[INFO] See README.md for detailed setup instructions")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
