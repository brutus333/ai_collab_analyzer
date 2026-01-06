from typing import List, Tuple, Dict, Any, Optional
from rapidfuzz import fuzz

class SimilarityGroup:
    """Represents a group of similar code elements."""
    def __init__(self, elements: List[Any], score: float):
        self.elements = elements
        self.score = score

class CodeSimilarityAnalyzer:
    """
    Analyzes similarity between code blocks.
    """
    
    def __init__(self, threshold: float = 80.0, min_length: int = 50):
        self.threshold = threshold
        self.min_length = min_length

    def normalize_code(self, code: str) -> str:
        """
        Normalizes code by removing comments, docstrings, and extra whitespace.
        """
        import re
        # Remove triple-quoted strings (docstrings/multi-line strings)
        code = re.sub(r'(""".*?"""|\'\'\'.*?\'\'\')', '', code, flags=re.DOTALL)
        # Remove single-line comments
        code = re.sub(r'#.*', '', code)
        # Remove all whitespace and newlines for a structural comparison
        return "".join(code.split())

    def calculate_similarity(self, code1: str, code2: str) -> float:
        """
        Calculates fuzzy similarity between two code blocks after normalization.
        """
        if not code1 or not code2:
            return 0.0
        
        if len(code1) < self.min_length or len(code2) < self.min_length:
            # Skip very small snippets as they lead to noise
            return 0.0

        norm1 = self.normalize_code(code1)
        norm2 = self.normalize_code(code2)
        
        if not norm1 or not norm2:
            return 0.0
            
        return fuzz.ratio(norm1, norm2)

    def find_near_duplicates(self, blocks: List[Tuple[str, str]], threshold: Optional[float] = None) -> List[Tuple[str, str, float]]:
        """
        Finds pairs of blocks that are near-duplicates.
        Input: List of (id, code_body)
        Output: List of (id1, id2, score)
        """
        t = threshold if threshold is not None else self.threshold
        results = []
        
        for i in range(len(blocks)):
            for j in range(i + 1, len(blocks)):
                id1, code1 = blocks[i]
                id2, code2 = blocks[j]
                if id1 == id2:
                    continue
                
                score = self.calculate_similarity(code1, code2)
                if score >= t:
                    results.append((id1, id2, score))
        
        return results
