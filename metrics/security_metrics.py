import ast
import re
from typing import List, Dict, Any

class SecurityMetricsCalculator:
    """
    Calculates security-related metrics using regex and AST heuristics.
    """
    
    # Common patterns for secrets (API keys, etc.)
    # Note: This is a basic set for demonstration and common cases
    SECRET_PATTERNS = [
        # Use string concatenation to avoid self-detection
        r"(?i)(api" + r"[_-]?key|access[_-]?token|secret[_-]?key|password|auth[_-]?token)['\"]?\s*[:=]\s*['\"]([a-zA-Z0-9_\-\.]{16,})['\"]",
        r"AIza" + r"[0-9A-Za-z-_]{35}", # Google API Key
        r"sk_" + r"[0-9a-zA-Z]{24}",    # Stripe Secret Key
        r"sq0atp-" + r"[0-9A-Za-z\-_]{22}", # Square Access Token
        r"---" + r"--BEGIN RSA PRIVATE KEY-----", # SSH Private Key
    ]

    VULNERABLE_FUNCTIONS = {
        'eval': 'eval() can execute arbitrary code.',
        'exec': 'exec() can execute arbitrary code.',
        'input': 'input() in Python 2 is equivalent to eval(). In Python 3 it is safe, but we flag for review.',
        'pickle.loads': 'pickle.loads() can lead to arbitrary code execution if used on untrusted data.',
        'yaml.load': 'yaml.load() without Loader=SafeLoader can execute arbitrary code.',
        'os.system': 'os.system() is prone to shell injection.',
        'subprocess.Popen': 'subprocess.Popen with shell=True is prone to shell injection.',
    }

    def detect_secrets(self, content: str) -> List[Dict[str, Any]]:
        """
        Scan code for potential secrets using regex.
        """
        secrets = []
        lines = content.splitlines()
        for i, line in enumerate(lines):
            for pattern in self.SECRET_PATTERNS:
                matches = re.finditer(pattern, line)
                for _ in matches:
                    secrets.append({
                        "line_number": i + 1,
                        "type": "potential_secret",
                        "description": "A potential secret or API key was found in the code."
                    })
        return secrets

    def inspect_vulnerable_calls(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """
        Scan AST for usage of potentially insecure functions.
        """
        vulnerabilities = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = ""
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    # Handle cases like pickle.loads
                    if isinstance(node.func.value, ast.Name):
                        func_name = f"{node.func.value.id}.{node.func.attr}"
                    else:
                        func_name = node.func.attr

                if func_name in self.VULNERABLE_FUNCTIONS:
                    # Special check for shell=True in subprocess
                    is_shell_true = False
                    if func_name == 'subprocess.Popen':
                        for keyword in node.keywords:
                            if keyword.arg == 'shell' and isinstance(keyword.value, ast.Constant) and keyword.value.value is True:
                                is_shell_true = True
                    
                    description = self.VULNERABLE_FUNCTIONS[func_name]
                    if is_shell_true:
                        description += " Specifically shell=True is detected."

                    vulnerabilities.append({
                        "line_number": node.lineno,
                        "function": func_name,
                        "description": description
                    })

        return vulnerabilities

    def analyze_module_security(self, tree: ast.AST) -> Dict[str, Any]:
        """
        Analyze high-level module security (e.g., use of dynamic imports).
        """
        stats = {
            "dynamic_imports": 0,
            "suspicious_imports": []
        }
        
        for node in ast.walk(tree):
            # Detect __import__ or importlib.import_module
            if isinstance(node, ast.Call):
                func_name = ""
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    func_name = node.func.attr
                
                if func_name in ('__import__', 'import_module'):
                    stats["dynamic_imports"] += 1
                    stats["suspicious_imports"].append({
                        "line_number": node.lineno,
                        "type": "dynamic_import"
                    })
                    
        return stats
