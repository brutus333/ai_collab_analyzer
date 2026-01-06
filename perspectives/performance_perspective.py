import ast
from ai_collab_analyzer.perspectives.base_perspective import BasePerspective
from ai_collab_analyzer.models.perspectives import PerspectiveResult, CodeEntity, DimensionScore, Finding, Severity, CodeLocation
from ai_collab_analyzer.metrics.performance_metrics import PerformanceMetricsCalculator

class PerformancePerspective(BasePerspective):
    """
    Analyzes code for potential performance issues and resource leaks.
    """
    
    def __init__(self):
        self.calculator = PerformanceMetricsCalculator()

    def get_name(self) -> str:
        return "Performance Analysis"

    def analyze(self, code_entity: CodeEntity) -> PerspectiveResult:
        """
        Analyze code for nested loops, recursion, and I/O efficiency.
        """
        code = code_entity.content
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return self._empty_result("Syntax error prevents performance analysis.")

        # 1. Calculate Dimensions
        nested_loops = self.calculator.detect_nested_loops(tree)
        recursion = self.calculator.detect_recursion(tree)
        io_in_loops = self.calculator.analyze_io_in_loops(tree)
        resource_issues = self.calculator.check_resource_management(tree)

        # Dimension: Algorithmic Efficiency (0-100)
        # Penalize deep nesting and recursion
        efficiency_penalty = (len(nested_loops) * 15) + (len(recursion) * 20)
        efficiency_score = max(0, 100 - efficiency_penalty)

        # Dimension: I/O Efficiency (0-100)
        io_penalty = len(io_in_loops) * 25
        io_score = max(0, 100 - io_penalty)

        # Dimension: Resource Management (0-100)
        resource_score = max(0, 100 - (len(resource_issues) * 30))

        dimensions = [
            DimensionScore("Algorithmic Efficiency", efficiency_score, weight=0.4, 
                           details={"nested_loops": len(nested_loops), "recursion": len(recursion)}),
            DimensionScore("I/O Efficiency", io_score, weight=0.3, 
                           details={"io_in_loops": len(io_in_loops)}),
            DimensionScore("Resource Management", resource_score, weight=0.3,
                           details={"resource_leaks": len(resource_issues)})
        ]

        # 2. Identify Findings
        findings = []
        recommendations = []

        # Nested loop findings
        for loop in nested_loops[:3]:
            findings.append(Finding(
                title=f"Potential O(n^{loop['depth']}) Complexity",
                description=f"Deeply nested {loop['type']} found at line {loop['line_number']}.",
                severity=Severity.HIGH if loop['depth'] > 2 else Severity.MEDIUM,
                location=CodeLocation(code_entity.filepath, loop['line_number'], loop['line_number']),
                recommendation="Consider optimizing the algorithm or using memoization."
            ))

        # I/O findings
        for io in io_in_loops[:3]:
            findings.append(Finding(
                title=f"Synchronous I/O in Loop: {io['operation']}",
                description=f"Performing I/O operation '{io['operation']}' inside a loop at line {io['line_number']}.",
                severity=Severity.HIGH,
                location=CodeLocation(code_entity.filepath, io['line_number'], io['line_number']),
                recommendation="Batch I/O operations or use asynchronous processing outside the loop."
            ))

        # Resource management findings
        for issue in resource_issues[:3]:
            findings.append(Finding(
                title=f"Insecure Resource Handling: {issue['operation']}",
                description=f"Resource '{issue['operation']}' opened at line {issue['line_number']} without a 'with' statement.",
                severity=Severity.MEDIUM,
                location=CodeLocation(code_entity.filepath, issue['line_number'], issue['line_number']),
                recommendation=issue['recommendation']
            ))

        if efficiency_score < 70:
            recommendations.append("Audit algorithmic hotpaths for O(n^2) or higher complexity.")
        
        if io_score < 100:
            recommendations.append("Optimize network and disk activity by reducing redundant operations in loops.")

        return PerspectiveResult(
            perspective_name=self.get_name(),
            score=self.calculate_score(dimensions),
            dimensions=dimensions,
            findings=findings,
            recommendations=recommendations
        )

