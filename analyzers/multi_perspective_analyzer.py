import os
from typing import List, Dict, Any, Tuple
from ai_collab_analyzer.analyzers.base_analyzer import BaseAnalyzer
from ai_collab_analyzer.core.repository import Repository
from ai_collab_analyzer.models.perspectives import MultiPerspectiveResult, PerspectiveResult, DimensionScore, CodeEntity, Finding, Severity
from ai_collab_analyzer.perspectives.structural_perspective import StructuralPerspective
from ai_collab_analyzer.perspectives.semantic_perspective import SemanticPerspective
from ai_collab_analyzer.perspectives.performance_perspective import PerformancePerspective
from ai_collab_analyzer.perspectives.security_perspective import SecurityPerspective

class MultiPerspectiveAnalyzer(BaseAnalyzer):
    """
    Coordinator for multi-dimensional code analysis.
    Runs multiple perspectives and aggregates results.
    """
    
    def __init__(self):
        super().__init__()
        self.perspectives = [
            StructuralPerspective(),
            SemanticPerspective(),
            PerformancePerspective(),
            SecurityPerspective()
        ]

    @property
    def name(self) -> str:
        return "Multi-Perspective Analyzer"

    @property
    def description(self) -> str:
        return "Comprehensive analysis of code from structural, semantic, and performance perspectives."

    def analyze(self, repository: Repository) -> MultiPerspectiveResult:
        """
        Analyze all files in the repository across all perspectives.
        """
        all_file_results: Dict[str, List[PerspectiveResult]] = {}
        
        # 1. Analyze Each File
        for filepath in repository.files:
            full_path = os.path.join(repository.path, filepath)
            if not os.path.exists(full_path) or not os.path.isfile(full_path):
                continue
                
            # Only analyze supported files (Python for now)
            if not filepath.endswith('.py'):
                continue

            try:
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                entity = CodeEntity(filepath=filepath, content=content)
                file_results = []
                for p in self.perspectives:
                    res = p.analyze(entity)
                    file_results.append(res)
                
                all_file_results[filepath] = file_results
            except Exception:
                continue

        # 2. Aggregate Results
        perspective_scores: Dict[str, List[float]] = {}
        perspective_dimensions: Dict[str, Dict[str, List[float]]] = {}
        perspective_recs: Dict[str, Set[str]] = {}
        all_findings: List[Finding] = []
        file_breakdown: Dict[str, Dict[str, float]] = {}

        for filepath, results in all_file_results.items():
            file_scores = {}
            for res in results:
                p_name = res.perspective_name
                if p_name not in perspective_scores:
                    perspective_scores[p_name] = []
                    perspective_dimensions[p_name] = {}
                    perspective_recs[p_name] = set()
                
                perspective_scores[p_name].append(res.score)
                file_scores[p_name] = res.score
                all_findings.extend(res.findings)
                perspective_recs[p_name].update(res.recommendations)

                # Aggregate dimensions
                for dim in res.dimensions:
                    if dim.name not in perspective_dimensions[p_name]:
                        perspective_dimensions[p_name][dim.name] = []
                    perspective_dimensions[p_name][dim.name].append(dim.score)
            
            file_breakdown[filepath] = file_scores

        # Average scores per perspective and dimension
        aggregate_perspective_results = []
        avg_perspective_scores = {}

        for p_name, scores in perspective_scores.items():
            avg_score = sum(scores)/len(scores) if scores else 0.0
            avg_perspective_scores[p_name] = avg_score
            
            # Aggregate dimensions for this perspective
            avg_dimensions = []
            for dim_name, dim_scores in perspective_dimensions[p_name].items():
                avg_dim_score = sum(dim_scores)/len(dim_scores) if dim_scores else 0.0
                avg_dimensions.append(DimensionScore(name=dim_name, score=avg_dim_score, weight=1.0)) # Weight is relative in aggregate
            
            aggregate_perspective_results.append(PerspectiveResult(
                perspective_name=p_name,
                score=avg_score,
                dimensions=avg_dimensions,
                findings=[], # We already have all_findings
                recommendations=list(perspective_recs[p_name])
            ))

        # Calculate final composite score
        composite_score = sum(avg_perspective_scores.values()) / len(avg_perspective_scores) if avg_perspective_scores else 100.0

        # Extract critical findings (HIGH or CRITICAL)
        critical_findings = [f for f in all_findings if f.severity in (Severity.HIGH, Severity.CRITICAL)]
        # Dedup or limit critical findings
        critical_findings.sort(key=lambda x: 1 if x.severity == Severity.CRITICAL else 2)

        return MultiPerspectiveResult(
            aggregate_scores=avg_perspective_scores,
            perspective_results=aggregate_perspective_results,
            composite_score=composite_score,
            critical_findings=critical_findings[:20], # Top 20 critical issues
            file_breakdown=file_breakdown
        )
