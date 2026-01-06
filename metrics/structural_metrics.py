import ast
from typing import Dict, Any, List, Optional

class StructuralMetricsCalculator:
    """
    Calculates structural metrics using Python's AST.
    """
    
    def calculate_cyclomatic_complexity(self, node: ast.AST) -> int:
        """
        Calculate cyclomatic complexity of a given AST node.
        Complexity = Number of decision points + 1.
        """
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.With, ast.AsyncWith,
                                 ast.And, ast.Or, ast.ExceptHandler, ast.Try, ast.Assert)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity

    def calculate_nesting_depth(self, node: ast.AST) -> int:
        """
        Calculate maximum nesting depth in the code.
        """
        max_depth = 0
        
        def walk_depth(n, current_depth):
            nonlocal max_depth
            if isinstance(n, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.With, ast.AsyncWith, ast.Try, ast.FunctionDef, ast.ClassDef)):
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            
            for child in ast.iter_child_nodes(n):
                walk_depth(child, current_depth)
        
        walk_depth(node, 0)
        return max_depth

    def get_function_metrics(self, code: str) -> List[Dict[str, Any]]:
        """
        Extract metrics for each function/method in the code.
        """
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return []
            
        metrics = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                metrics.append({
                    "name": node.name,
                    "type": "function",
                    "complexity": self.calculate_cyclomatic_complexity(node),
                    "nesting": self.calculate_nesting_depth(node),
                    "line_number": node.lineno
                })
        return metrics

    def calculate_maintainability_index(self, complexity: int, loc: int, comment_weight: float = 0.2) -> float:
        """
        A simplified version of the Maintainability Index.
        MI = 171 - 5.2 * ln(volume) - 0.23 * (cyclomatic complexity) - 16.2 * ln(loc) + 50 * sin(sqrt(2.4 * perCM))
        We use a simpler heuristic for now.
        """
        if loc == 0: return 100.0
        # 100 - (Complexity * 2) - (LOC / 10) + (Bonus if comments exist)
        score = 100.0 - (complexity * 1.5) - (loc / 20.0)
        return min(100.0, max(0.0, score))
