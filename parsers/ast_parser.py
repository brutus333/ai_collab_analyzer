import ast
from typing import List, Dict, Any, Optional

class CodeNode:
    """Represents a structural element in the code (class or function)."""
    def __init__(self, name: str, type: str, start_line: int, end_line: int, body: str):
        self.name = name
        self.type = type
        self.start_line = start_line
        self.end_line = end_line
        self.body = body

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "body": self.body
        }

class PythonASTParser:
    """
    Parses Python source code and extracts structural elements.
    """
    
    def parse(self, code: str) -> List[CodeNode]:
        """
        Parses Python code and returns a list of CodeNodes.
        """
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return []

        nodes = []
        lines = code.splitlines()

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                node_type = "function" if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) else "class"
                
                # Get start and end lines
                start_line = node.lineno
                # end_line is not directly available in early python versions, 
                # but we can estimate or use end_lineno if available (Python 3.8+)
                end_line = getattr(node, "end_lineno", start_line)
                
                # Extract body
                body = "\n".join(lines[start_line-1:end_line])
                
                nodes.append(CodeNode(
                    name=node.name,
                    type=node_type,
                    start_line=start_line,
                    end_line=end_line,
                    body=body
                ))
        
        return nodes
