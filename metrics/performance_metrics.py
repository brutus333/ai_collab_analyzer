import ast
from typing import List, Dict, Any, Optional

class PerformanceMetricsCalculator:
    """
    Calculates performance-related metrics using AST heuristics.
    """
    
    IO_KEYWORDS = {
        'open', 'read', 'write', 'requests', 'get', 'post', 'socket', 'connection', 
        'connect', 'execute', 'query', 'cursor', 'send', 'recv', 'download', 'upload'
    }

    def detect_nested_loops(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """
        Identify deeply nested loops (potential O(n^k) complexity).
        """
        hotspots = []
        
        def check_nesting(node, depth):
            if isinstance(node, (ast.For, ast.While, ast.AsyncFor)):
                depth += 1
                if depth >= 2:
                    hotspots.append({
                        "line_number": node.lineno,
                        "depth": depth,
                        "type": type(node).__name__
                    })
                
                for child in ast.iter_child_nodes(node):
                    check_nesting(child, depth)
            else:
                for child in ast.iter_child_nodes(node):
                    check_nesting(child, depth)

        check_nesting(tree, 0)
        return hotspots

    def detect_recursion(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """
        Detect simple direct recursion.
        """
        recursion_points = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_name = node.name
                for child in ast.walk(node):
                    if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                        if child.func.id == func_name:
                            recursion_points.append({
                                "name": func_name,
                                "line_number": child.lineno
                            })
                            break
        return recursion_points

    def analyze_io_in_loops(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """
        Detect I/O operations inside loops.
        """
        io_in_loops = []
        
        def find_io(node, in_loop=False):
            if isinstance(node, (ast.For, ast.While, ast.AsyncFor)):
                for child in ast.iter_child_nodes(node):
                    find_io(child, in_loop=True)
            elif isinstance(node, ast.Call) and in_loop:
                func_name = ""
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    func_name = node.func.attr
                
                if any(keyword in func_name.lower() for keyword in self.IO_KEYWORDS):
                    io_in_loops.append({
                        "operation": func_name,
                        "line_number": node.lineno
                    })
                
                # Still continue walk as there might be nested loops
                for child in ast.iter_child_nodes(node):
                    find_io(child, in_loop)
            else:
                for child in ast.iter_child_nodes(node):
                    find_io(child, in_loop)

        find_io(tree)
        return io_in_loops

    def check_resource_management(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """
        Detect unclosed resources (e.g., open() without 'with').
        """
        issues = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'open':
                # Check if this call is an expression or assignment not in a 'with'
                # This is a basic heuristic
                parent = self._get_parent(tree, node)
                if not isinstance(parent, ast.withitem):
                    # Check if it's assigned to a variable that might be closed later
                    # but 'with' is preferred.
                    issues.append({
                        "operation": "open",
                        "line_number": node.lineno,
                        "recommendation": "Use 'with' statement for resource management."
                    })
        return issues

    def _get_parent(self, root, target):
        """Helper to find parent of a node."""
        for node in ast.walk(root):
            for child in ast.iter_child_nodes(node):
                if child is target:
                    return node
        return None
