import ast
from typing import List, Dict, Any
from ai_collab_analyzer.perspectives.base_perspective import BasePerspective
from ai_collab_analyzer.models.perspectives import PerspectiveResult, CodeEntity, DimensionScore, Finding, Severity, CodeLocation
from ai_collab_analyzer.metrics.structural_metrics import StructuralMetricsCalculator

class StructuralPerspective(BasePerspective):
    """
    Analyzes code structure, complexity, and modularity.
    """
    
    def __init__(self):
        self.calculator = StructuralMetricsCalculator()

    def get_name(self) -> str:
        return "Structural Analysis"

    def analyze(self, code_entity: CodeEntity) -> PerspectiveResult:
        """
        Analyze code for complexity and modularity.
        """
        code = code_entity.content
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return self._empty_result("Syntax error prevents structural analysis.")

        # 1. Calculate Dimensions
        func_metrics = self.calculator.get_function_metrics(code)
        avg_complexity = sum(m['complexity'] for m in func_metrics) / len(func_metrics) if func_metrics else 1
        max_complexity = max((m['complexity'] for m in func_metrics), default=1)
        max_nesting = self.calculator.calculate_nesting_depth(tree)
        lines_of_code = len(code.splitlines())

        # Dimension: Complexity (0-100)
        # 10 is good, 30+ is critical
        complexity_score = max(0, 100 - (avg_complexity * 5) - (max_complexity * 2))
        
        # Dimension: Modularity (0-100)
        # Based on function sizes and count
        func_count = len(func_metrics)
        avg_func_size = lines_of_code / func_count if func_count > 0 else lines_of_code
        modularity_score = max(0, 100 - (avg_func_size / 2) if avg_func_size > 50 else 100)

        # Dimension: Maintainability
        mi_score = self.calculator.calculate_maintainability_index(int(avg_complexity), lines_of_code)

        dimensions = [
            DimensionScore("Complexity", complexity_score, weight=0.4, details={"avg_complexity": avg_complexity, "max_complexity": max_complexity}),
            DimensionScore("Modularity", modularity_score, weight=0.3, details={"avg_func_size": avg_func_size, "func_count": func_count}),
            DimensionScore("Maintainability", mi_score, weight=0.3)
        ]

        # 2. Identify Findings
        findings = []
        recommendations = []
        
        for m in func_metrics:
            if m['complexity'] > 15:
                findings.append(Finding(
                    title=f"High Complexity: {m['name']}",
                    description=f"Function '{m['name']}' has a cyclomatic complexity of {m['complexity']}.",
                    severity=Severity.HIGH if m['complexity'] > 25 else Severity.MEDIUM,
                    location=CodeLocation(code_entity.filepath, m['line_number'], m['line_number'], m['name']),
                    recommendation="Consider breaking this function into smaller, more focused units."
                ))
            if m['nesting'] > 4:
                findings.append(Finding(
                    title=f"Deep Nesting: {m['name']}",
                    description=f"Function '{m['name']}' has a nesting depth of {m['nesting']}.",
                    severity=Severity.MEDIUM,
                    location=CodeLocation(code_entity.filepath, m['line_number'], m['line_number'], m['name']),
                    recommendation="Reduce nesting by using guard clauses or extracting sub-logic."
                ))

        if mi_score < 40:
            recommendations.append("Prioritize refactoring structural hotspots to improve long-term maintainability.")

        return PerspectiveResult(
            perspective_name=self.get_name(),
            score=self.calculate_score(dimensions),
            dimensions=dimensions,
            findings=findings,
            recommendations=recommendations
        )

