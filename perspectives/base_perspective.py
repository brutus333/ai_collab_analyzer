from abc import ABC, abstractmethod
from typing import List, Optional, Any
from ai_collab_analyzer.models.perspectives import PerspectiveResult, CodeEntity, DimensionScore

class BasePerspective(ABC):
    """
    Abstract base class for all analysis perspectives.
    """
    
    @abstractmethod
    def get_name(self) -> str:
        """Return the name of the perspective."""
        pass
        
    @abstractmethod
    def analyze(self, code_entity: CodeEntity) -> PerspectiveResult:
        """Performs the actual analysis on a code entity."""
        pass

    def calculate_score(self, dimensions: List[DimensionScore]) -> float:
        """
        Calculates the weighted score based on dimensions.
        """
        if not dimensions:
            return 100.0
            
        total_weight = sum(d.weight for d in dimensions)
        if total_weight == 0:
            return sum(d.score for d in dimensions) / len(dimensions)
            
        weighted_score = sum(d.score * d.weight for d in dimensions) / total_weight
        return min(100.0, max(0.0, weighted_score))
