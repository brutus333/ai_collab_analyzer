from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime

@dataclass
class BenchmarkResult:
    """Represents how a repository compares to industry standards."""
    metric_name: str
    repo_value: float
    industry_avg: float
    percentile: float
    rating: str  # e.g., 'Excellence', 'Standard', 'Underperforming'

@dataclass
class PortfolioMetrics:
    """Metrics aggregated across multiple repositories."""
    total_repos: int
    avg_health_score: float
    avg_coherence_score: float
    avg_risk_score: float
    top_risky_files: List[Dict[str, Any]] = field(default_factory=list)
    repo_comparisons: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)
