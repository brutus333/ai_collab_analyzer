import ast
from ai_collab_analyzer.perspectives.base_perspective import BasePerspective
from ai_collab_analyzer.models.perspectives import PerspectiveResult, CodeEntity, DimensionScore, Finding, Severity, CodeLocation
from ai_collab_analyzer.metrics.security_metrics import SecurityMetricsCalculator

class SecurityPerspective(BasePerspective):
    """
    Analyzes code for security vulnerabilities and exposed secrets.
    """
    
    def __init__(self):
        self.calculator = SecurityMetricsCalculator()

    def get_name(self) -> str:
        return "Security Analysis"

    def analyze(self, code_entity: CodeEntity) -> PerspectiveResult:
        """
        Analyze code for secrets and insecure patterns.
        """
        code = code_entity.content
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return self._empty_result("Syntax error prevents security analysis.")

        # 1. Calculate Dimensions
        secrets = self.calculator.detect_secrets(code)
        vulnerabilities = self.calculator.inspect_vulnerable_calls(tree)
        module_stats = self.calculator.analyze_module_security(tree)

        # Dimension: Secret Hygiene (0-100)
        # Any secret is a critical failure (0 score)
        secret_score = max(0, 100 - (len(secrets) * 100))

        # Dimension: Vulnerability Free (0-100)
        # Score decreases based on number of insecure calls
        vuln_score = max(0, 100 - (len(vulnerabilities) * 20))

        # Dimension: Module Security
        # Penalize dynamic imports or suspicious patterns
        module_score = max(0, 100 - (module_stats["dynamic_imports"] * 10))

        dimensions = [
            DimensionScore("Secret Hygiene", float(secret_score), weight=0.5, 
                           details={"secrets_found": len(secrets)}),
            DimensionScore("Insecure Patterns", float(vuln_score), weight=0.3, 
                           details={"vuln_calls": len(vulnerabilities)}),
            DimensionScore("Import Security", float(module_score), weight=0.2,
                           details={"dynamic_imports": module_stats["dynamic_imports"]})
        ]

        # 2. Identify Findings
        findings = []
        recommendations = []

        # Secret findings - CRITICAL
        for secret in secrets:
            findings.append(Finding(
                title="Exposed Secret or API Key",
                description=secret["description"],
                severity=Severity.CRITICAL,
                location=CodeLocation(code_entity.filepath, secret["line_number"], secret["line_number"]),
                recommendation="Immediately revoke this key and move it to an environment variable or secret manager."
            ))

        # Vulnerability findings
        for vuln in vulnerabilities:
            findings.append(Finding(
                title=f"Insecure Function Call: {vuln['function']}",
                description=vuln["description"],
                severity=Severity.HIGH,
                location=CodeLocation(code_entity.filepath, vuln["line_number"], vuln["line_number"]),
                recommendation=f"Avoid using {vuln['function']} with untrusted data. Use safer alternatives."
            ))

        # Module findings
        for imp in module_stats["suspicious_imports"]:
            findings.append(Finding(
                title="Dynamic Module Import",
                description="Use of dynamic imports detected, which can be a vector for malicious code injection.",
                severity=Severity.MEDIUM,
                location=CodeLocation(code_entity.filepath, imp["line_number"], imp["line_number"]),
                recommendation="Prefer static imports whenever possible."
            ))

        if secret_score == 0:
            recommendations.append("CRITICAL: Remove hardcoded secrets and purge them from git history using BFG or git-filter-repo.")
        
        if vuln_score < 100:
            recommendations.append("Replace insecure function calls (eval, exec, system) with safer alternatives like AST parsing or subprocess with shell=False.")

        return PerspectiveResult(
            perspective_name=self.get_name(),
            score=self.calculate_score(dimensions),
            dimensions=dimensions,
            findings=findings,
            recommendations=recommendations
        )

