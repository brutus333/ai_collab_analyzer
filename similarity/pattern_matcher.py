import ast
from typing import List, Dict, Any

class PatternMatcher:
    """
    Identifies structural patterns in Python code.
    """
    
    def extract_traits(self, code: str) -> Dict[str, Any]:
        """
        Extracts structural traits from code to identify implementation style.
        """
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return {}

        traits = {
            "has_list_comp": 0,
            "has_for_loop": 0,
            "has_try_except": 0,
            "has_nested_functions": 0,
            "async_count": 0,
            "docstring_present": False
        }

        for node in ast.walk(tree):
            if isinstance(node, ast.ListComp):
                traits["has_list_comp"] += 1
            elif isinstance(node, ast.For):
                traits["has_for_loop"] += 1
            elif isinstance(node, ast.Try):
                traits["has_try_except"] += 1
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if isinstance(node, ast.AsyncFunctionDef):
                    traits["async_count"] += 1
                # Check for nested functions
                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        traits["has_nested_functions"] += 1
                
                # Check for docstring
                if ast.get_docstring(node):
                    traits["docstring_present"] = True

        return traits

    def calculate_variance(self, traits_list: List[Dict[str, Any]]) -> float:
        """
        Calculates a simple 'variance' score between implementation styles.
        0.0 means perfectly consistent, higher means less consistent.
        """
        if not traits_list:
            return 0.0
            
        # Simplified: check how many have docstrings vs not
        docstrings = [t.get("docstring_present", False) for t in traits_list]
        doc_count = sum(docstrings)
        
        if doc_count == 0 or doc_count == len(traits_list):
            return 0.0
        
        return 1.0 # Some variation exists
