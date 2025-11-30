"""
PDF parsing utilities for extracting text and sections from research papers.
"""

import pdfplumber
import re
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PaperParser:
    """Parse research papers and extract structured content."""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.full_text = ""
        self.sections = {}
        
    def extract_all_text(self) -> str:
        """Extract all text from PDF."""
        try:
            text_content = []
            with pdfplumber.open(self.pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_content.append(text)
            
            self.full_text = "\n\n".join(text_content)
            logger.info(f"Extracted {len(self.full_text)} characters from PDF")
            return self.full_text
            
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            raise
    
    def extract_sections(self) -> Dict[str, str]:
        """
        Extract common paper sections.
        Returns dict with keys: abstract, introduction, methods, results, conclusion
        """
        if not self.full_text:
            self.extract_all_text()
        
        sections = {}
        
        # Pattern for Abstract
        abstract_match = re.search(
            r"(?i)abstract\s*\n(.*?)(?=\n\s*(?:introduction|keywords|\d+\s+introduction))",
            self.full_text,
            re.DOTALL
        )
        if abstract_match:
            sections["abstract"] = abstract_match.group(1).strip()[:2000]
        
        # Pattern for Introduction
        intro_match = re.search(
            r"(?i)(?:^|\n)\s*(?:\d+\.?\s*)?introduction\s*\n(.*?)(?=\n\s*(?:\d+\.?\s*)?(?:related work|background|method))",
            self.full_text,
            re.DOTALL
        )
        if intro_match:
            sections["introduction"] = intro_match.group(1).strip()[:3000]
        
        # Pattern for Methods/Methodology
        methods_match = re.search(
            r"(?i)(?:^|\n)\s*(?:\d+\.?\s*)?(?:method|methodology|approach|model)\s*\n(.*?)(?=\n\s*(?:\d+\.?\s*)?(?:experiment|result|evaluation))",
            self.full_text,
            re.DOTALL
        )
        if methods_match:
            sections["methods"] = methods_match.group(1).strip()[:4000]
        
        # Pattern for Results/Experiments
        results_match = re.search(
            r"(?i)(?:^|\n)\s*(?:\d+\.?\s*)?(?:result|experiment)\s*\n(.*?)(?=\n\s*(?:\d+\.?\s*)?(?:discussion|conclusion|related work))",
            self.full_text,
            re.DOTALL
        )
        if results_match:
            sections["results"] = results_match.group(1).strip()[:3000]
        
        # Pattern for Conclusion
        conclusion_match = re.search(
            r"(?i)(?:^|\n)\s*(?:\d+\.?\s*)?conclusion\s*\n(.*?)(?=\n\s*(?:reference|acknowledgment|$))",
            self.full_text,
            re.DOTALL
        )
        if conclusion_match:
            sections["conclusion"] = conclusion_match.group(1).strip()[:2000]
        
        # If no sections found, create from first few pages
        if not sections:
            sections["content"] = self.full_text[:5000]
        
        self.sections = sections
        logger.info(f"Extracted {len(sections)} sections")
        return sections
    
    def get_section(self, section_name: str) -> Optional[str]:
        """Get a specific section by name."""
        if not self.sections:
            self.extract_sections()
        return self.sections.get(section_name.lower())
    
    def search_content(self, query: str, context_chars: int = 500) -> List[Dict]:
        """
        Search for a query in the paper and return matches with context.
        """
        if not self.full_text:
            self.extract_all_text()
        
        results = []
        query_lower = query.lower()
        text_lower = self.full_text.lower()
        
        # Find all occurrences
        start = 0
        while True:
            pos = text_lower.find(query_lower, start)
            if pos == -1:
                break
            
            # Get context around match
            context_start = max(0, pos - context_chars)
            context_end = min(len(self.full_text), pos + len(query) + context_chars)
            
            results.append({
                "position": pos,
                "context": self.full_text[context_start:context_end],
                "match": self.full_text[pos:pos + len(query)]
            })
            
            start = pos + 1
        
        logger.info(f"Found {len(results)} matches for '{query}'")
        return results
    
    def get_summary(self) -> Dict[str, str]:
        """Get a quick summary with title, abstract, and key points."""
        if not self.sections:
            self.extract_sections()
        
        summary = {
            "abstract": self.sections.get("abstract", "Not found")[:1000],
            "introduction_preview": self.sections.get("introduction", "Not found")[:800],
            "conclusion": self.sections.get("conclusion", "Not found")[:800],
        }
        
        return summary