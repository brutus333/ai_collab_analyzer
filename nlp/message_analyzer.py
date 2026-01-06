import re
from typing import List, Dict, Any, Optional
from enum import Enum

class Intent(Enum):
    FEATURE_ADD = "feature_add"
    BUG_FIX = "bug_fix"
    REGENERATION = "regeneration"
    REFACTOR = "refactor"
    CLARIFICATION = "clarification"
    UNKNOWN = "unknown"

class MessageAnalyzer:
    """
    Analyzes commit messages for intent, clarity, and sentiment markers.
    """
    
    INTENT_PATTERNS = {
        Intent.FEATURE_ADD: [r"\badd\b", r"\bfeat\b", r"\bimplement\b", r"\bnew\b"],
        Intent.BUG_FIX: [r"\bfix\b", r"\bbug\b", r"\bissue\b", r"\berror\b", r"\bpatch\b"],
        Intent.REGENERATION: [r"\bregen\b", r"\bregenerate\b", r"\btry again\b", r"\bre-run\b"],
        Intent.REFACTOR: [r"\brefactor\b", r"\bclean\b", r"\breorganize\b", r"\boptimize\b"],
        Intent.CLARIFICATION: [r"\bclarify\b", r"\bexplain\b", r"\bcomment\b", r"\bdoc\b"]
    }

    FRUSTRATION_MARKERS = [
        r"\bwhy\b", r"\bstupid\b", r"\bwrong\b", r"\bdoesn't work\b", 
        r"\bbroken\b", r"\bagain\b!", r"\bfixing the fix\b"
    ]

    def analyze(self, message: str) -> Dict[str, Any]:
        """
        Performs full analysis on a message.
        """
        lower_msg = message.lower()
        
        return {
            "intent": self.classify_intent(lower_msg),
            "frustration_level": self.detect_frustration(lower_msg),
            "keywords": self.extract_keywords(lower_msg),
            "clarity_score": self.calculate_clarity(message)
        }

    def classify_intent(self, message: str) -> Intent:
        for intent, patterns in self.INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, message):
                    return intent
        return Intent.UNKNOWN

    def detect_frustration(self, message: str) -> float:
        """Returns a score from 0.0 to 1.0."""
        matches = 0
        for pattern in self.FRUSTRATION_MARKERS:
            if re.search(pattern, message):
                matches += 1
        
        return min(1.0, matches * 0.3)

    def extract_keywords(self, message: str) -> List[str]:
        # Simple stop-word filter and word extraction
        words = re.findall(r"\w+", message)
        stop_words = {"the", "a", "an", "and", "or", "in", "on", "at", "to", "for", "with", "is"}
        return [w for w in words if len(w) > 3 and w not in stop_words]

    def calculate_clarity(self, message: str) -> float:
        """Simple clarity score based on length and structure."""
        if not message:
            return 0.0
        
        # Prefer messages with at least 5 words and no excessive punctuation
        words = message.split()
        score = min(1.0, len(words) / 10.0)
        
        # Subjective penalty for single-word messages
        if len(words) < 3:
            score *= 0.5
            
        return score
