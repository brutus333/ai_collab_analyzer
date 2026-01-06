from dataclasses import dataclass
from typing import Any, Dict, List
from ai_collab_analyzer.analyzers.base_analyzer import BaseAnalyzer
from ai_collab_analyzer.core.repository import Repository
from ai_collab_analyzer.metrics.basic_metrics import MetricsCalculator

@dataclass
class FileHotspot:
    """
    Represents a file identified as a hotspot.
    """
    filepath: str
    change_count: int
    churn_rate: float

class HealthAnalyzer(BaseAnalyzer):
    """
    Analyzes the overall health of the repository using basic metrics.
    """
    
    def __init__(self):
        super().__init__()
        self.metrics_calculator = MetricsCalculator()
        
    @property
    def name(self) -> str:
        return "Repository Health Analyzer"
        
    @property
    def description(self) -> str:
        return "Calculates repository health metrics and identifies hotspots."
        
    def analyze(self, repository: Repository) -> Dict[str, Any]:
        """
        Perform health analysis.
        Returns dictionary containing score and hotspots.
        """
        hotspots = self.identify_hotspots(repository)
        score = self.calculate_health_score(repository, hotspots)
        
        return {
            "health_score": score,
            "hotspots": hotspots,
            "summary": f"Repository Health Score: {score:.2f}/100"
        }
        
    def identify_hotspots(self, repository: Repository) -> List[FileHotspot]:
        """
        Identify top hotspots in the repository.
        """
        # Get raw hotspots (filepath, count) from metrics
        raw_hotspots = self.metrics_calculator.calculate_file_hotspots(repository, top_n=10)
        
        hotspots = []
        for filepath, count in raw_hotspots:
            history = repository.get_file_history(filepath)
            churn = history.get_churn_rate() if history else 0.0
            
            hotspots.append(FileHotspot(filepath, count, churn))
            
        return hotspots
        
    def calculate_health_score(self, repository: Repository, hotspots: List[FileHotspot]) -> float:
        """
        Calculate a heuristic health score (0-100).
        Simple heuristic: Higher churn and more hotspots reduces score.
        """
        base_score = 100.0
        
        # Penalize for number of intense hotspots
        # If we have files with very high churn, reduce score
        if not hotspots:
            return 100.0
            
        penalty = 0.0
        for hotspot in hotspots:
            # Simple penalty logic: logic can be refined
            # If churn > 50 lines/commit, penalize
            if hotspot.churn_rate > 50:
                penalty += 5.0
            elif hotspot.churn_rate > 20:
                penalty += 2.0
                
            # If change frequency is very high (relative to repo age? not available yet)
            if hotspot.change_count > 20:
                penalty += 2.0
                
        # Cap penalty
        return max(0.0, base_score - penalty)
