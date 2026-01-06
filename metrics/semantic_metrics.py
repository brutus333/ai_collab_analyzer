import ast
import re
from typing import List, Dict, Any, Set

class SemanticMetricsCalculator:
    """
    Calculates semantic metrics like naming quality and documentation coverage.
    """
    
    GENERIC_NAMES = {
        'data', 'temp', 'tmp', 'val', 'value', 'obj', 'object', 'item', 'list', 'dict',
        'var', 'x', 'y', 'z', 'i', 'j', 'k', 'handle', 'manager', 'process'
    }

    def analyze_identifiers(self, tree: ast.AST) -> Dict[str, Any]:
        """
        Extract and analyze all identifiers (variables, functions, classes).
        """
        identifiers = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                identifiers.append((node.id, "variable", node.lineno))
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                identifiers.append((node.name, "function", node.lineno))
            elif isinstance(node, ast.ClassDef):
                identifiers.append((node.name, "class", node.lineno))
            elif isinstance(node, ast.arg):
                identifiers.append((node.arg, "argument", node.lineno))

        stats = {
            "total_count": len(identifiers),
            "generic_count": 0,
            "short_count": 0,
            "long_count": 0,
            "generic_list": [],
            "short_list": []
        }

        for name, itype, line in identifiers:
            # Check for generic names
            if name.lower() in self.GENERIC_NAMES:
                stats["generic_count"] += 1
                stats["generic_list"].append((name, itype, line))
            
            # Check for overly short names (ignoring common loop variables if they are 'i', 'j', 'k')
            if len(name) < 3 and name.lower() not in {'i', 'j', 'k', 'u', 'v', 'x', 'y'}:
                stats["short_count"] += 1
                stats["short_list"].append((name, itype, line))
                
            # Check for overly long names
            if len(name) > 35:
                stats["long_count"] += 1

        return stats

    def calculate_documentation_coverage(self, tree: ast.AST) -> Dict[str, Any]:
        """
        Calculate docstring coverage for classes and functions.
        """
        total_documentable = 0
        documented_count = 0
        missing = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                total_documentable += 1
                doc = ast.get_docstring(node)
                if doc and doc.strip():
                    documented_count += 1
                else:
                    missing.append((node.name, type(node).__name__, node.lineno))

        coverage = (documented_count / total_documentable) if total_documentable > 0 else 1.0
        return {
            "coverage": coverage,
            "documented_count": documented_count,
            "total_count": total_documentable,
            "missing": missing
        }

    def calculate_comment_ratio(self, code: str) -> float:
        """
        Calculate ratio of comment lines to code lines.
        """
        lines = code.splitlines()
        if not lines: return 0.0
        
        comment_lines = 0
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('#'):
                comment_lines += 1
                
        return comment_lines / len(lines)
