from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional

@dataclass
class DuplicationCluster:
    """Represents a set of near-duplicate code blocks."""
    cluster_id: str
    files: List[str]
    similarity_score: float
    code_snippet: str
    recommendation: str

@dataclass
class DriftEvent:
    """Represents a detected change in implementation style over time."""
    timestamp: datetime
    filepath: str
    drift_type: str
    description: str
    severity: float  # 0.0 to 1.0

@dataclass
class CoherenceAnalysisResult:
    """Final results of the coherence analysis."""
    coherence_score: float  # 0 to 100
    duplication_clusters: List[DuplicationCluster] = field(default_factory=list)
    drift_events: List[DriftEvent] = field(default_factory=list)
    summary: str = ""
