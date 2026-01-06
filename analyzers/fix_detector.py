from enum import Enum
from typing import List, Set
import re
from ai_collab_analyzer.core.commit import Commit

class CommitType(Enum):
    FEATURE = "FEATURE"
    FIX = "FIX"
    REFACTOR = "REFACTOR"
    REGENERATION = "REGENERATION"
    UNKNOWN = "UNKNOWN"

class FixDetector:
    """
    Analyzes commit messages to detect fixes and classify commit types.
    """
    
    def __init__(self):
        self.fix_keywords = {
            "fix", "fixes", "fixed", "fixing",
            "bug", "issue", "error", "defect",
            "correct", "correction", "corrected",
            "patch", "patched",
            "resolve", "resolved",
            "oops", "whoops", "mistake", "typo"
        }
        
        self.feature_keywords = {
            "feat", "feature", "add", "added", "adding",
            "implement", "implemented", "new", "create"
        }
        
        self.refactor_keywords = {
            "refactor", "refactored", "refactoring",
            "clean", "cleanup", "structure", "restructure",
            "move", "rename"
        }
        
        self.regen_keywords = {
            "regenerate", "regenerated", "regeneration",
            "rewrite", "rewritten", "generated"
        }
        
    def extract_keywords(self, message: str) -> Set[str]:
        """
        Extract normalized keywords from message.
        """
        if not message:
            return set()
            
        # Convert to lower, remove special chars
        clean_msg = re.sub(r'[^a-zA-Z0-9\s]', ' ', message.lower())
        return set(clean_msg.split())
        
    def is_fix_commit(self, commit: Commit) -> bool:
        """
        Determine if a commit is likely a fix.
        """
        keywords = self.extract_keywords(commit.message)
        return not keywords.isdisjoint(self.fix_keywords)
        
    def classify_commit(self, commit: Commit) -> CommitType:
        """
        Classify a commit into a type.
        """
        keywords = self.extract_keywords(commit.message)
        
        # Check priority: Regeneration > Fix > Feature > Refactor
        # (Arbitrary priority, but regeneration is specific)
        
        if not keywords.isdisjoint(self.regen_keywords):
            return CommitType.REGENERATION
            
        if not keywords.isdisjoint(self.fix_keywords):
            return CommitType.FIX
            
        if not keywords.isdisjoint(self.feature_keywords):
            return CommitType.FEATURE
            
        if not keywords.isdisjoint(self.refactor_keywords):
            return CommitType.REFACTOR
            
        return CommitType.UNKNOWN
