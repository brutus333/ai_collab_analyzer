import ast
from ai_collab_analyzer.perspectives.base_perspective import BasePerspective
from ai_collab_analyzer.models.perspectives import PerspectiveResult, CodeEntity, DimensionScore, Finding, Severity, CodeLocation
from ai_collab_analyzer.metrics.semantic_metrics import SemanticMetricsCalculator

class SemanticPerspective(BasePerspective):
    """
    Analyzes code meaning, naming quality, and documentation.
    """
    
    def __init__(self):
        self.calculator = SemanticMetricsCalculator()

    def get_name(self) -> str:
        return "Semantic Analysis"

    def analyze(self, code_entity: CodeEntity) -> PerspectiveResult:
        """
        Analyze code for naming clarity and documentation completeness.
        """
        code = code_entity.content
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return self._empty_result("Syntax error prevents semantic analysis.")

        # 1. Calculate Dimensions
        naming_stats = self.calculator.analyze_identifiers(tree)
        doc_stats = self.calculator.calculate_documentation_coverage(tree)
        comment_ratio = self.calculator.calculate_comment_ratio(code)

        # Dimension: Naming Quality (0-100)
        # Penalize generic and short names
        total_idents = naming_stats["total_count"]
        if total_idents > 0:
            naming_penalty = (naming_stats["generic_count"] * 10) + (naming_stats["short_count"] * 5)
            naming_score = max(0, 100 - (naming_penalty / total_idents * 20)) # Weighted penalty
        else:
            naming_score = 100.0

        # Dimension: Documentation (0-100)
        doc_score = doc_stats["coverage"] * 100.0

        # Dimension: Clarity
        # Combination of comment ratio (ideal 10-20%) and naming
        clarity_score = naming_score * 0.7 + (min(comment_ratio, 0.2) / 0.2 * 30.0)

        dimensions = [
            DimensionScore("Naming Quality", naming_score, weight=0.4, 
                           details={"generic_names": naming_stats["generic_count"], "short_names": naming_stats["short_count"]}),
            DimensionScore("Documentation", doc_score, weight=0.4,
                           details={"total_documentable": doc_stats["total_count"], "documented": doc_stats["documented_count"]}),
            DimensionScore("Code Clarity", clarity_score, weight=0.2, details={"comment_ratio": comment_ratio})
        ]

        # 2. Identify Findings
        findings = []
        recommendations = []

        # Generic name findings
        for name, itype, line in naming_stats["generic_list"][:5]:
            findings.append(Finding(
                title=f"Generic Identifier: {name}",
                description=f"The {itype} '{name}' is too generic and doesn't convey clear intent.",
                severity=Severity.LOW,
                location=CodeLocation(code_entity.filepath, line, line, name),
                recommendation="Use more descriptive names that reflect the domain or data contents."
            ))

        # Documentation findings
        if doc_score < 50 and doc_stats["total_count"] > 2:
            findings.append(Finding(
                title="Low Documentation Coverage",
                description=f"Only {doc_score:.1f}% of classes/functions are documented with docstrings.",
                severity=Severity.MEDIUM,
                recommendation="Add docstrings to public classes and functions to improve maintainability."
            ))

        if naming_score < 60:
            recommendations.append("Audit variable and function names to ensure they follow meaningful domain-driven naming.")
        
        if doc_score < 70:
            recommendations.append("Increase docstring coverage, especially for entry point functions.")

        return PerspectiveResult(
            perspective_name=self.get_name(),
            score=self.calculate_score(dimensions),
            dimensions=dimensions,
            findings=findings,
            recommendations=recommendations
        )

    def _empty_result(self, message: str) -> PerspectiveResult:
        return PerspectiveResult(
            perspective_name=self.get_name(),
            score=0,
            dimensions=[],
            findings=[Finding("Analysis Error", message, Severity.LOW)],
            recommendations=[]
        )
