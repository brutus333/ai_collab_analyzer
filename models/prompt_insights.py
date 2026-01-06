from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime

@dataclass
class LearningCurve:
    """Tracks improvement in prompt efficiency over time."""
    improvement_rate: float
    skill_level: str  # beginner, intermediate, advanced
    plateau_detected: bool
    efficiency_trend: List[float] = field(default_factory=list)

@dataclass
class PromptEfficiencyScore:
    """Measures how effective prompts are in generating stable code."""
    overall_score: float  # 0 to 100
    first_time_success_rate: float
    avg_revisions_per_feature: float

@dataclass
class InstructionalCorrelation:
    """Correlates doc instructions with code quality improvements."""
    instruction: str
    impact_score: float # % change in first-time success
    context: str # e.g., "Bug fixes reduced by 15% after this rule"
    commit_hash: str

@dataclass
class PromptInsightResult:
    """Aggregated insights for the report."""
    total_prompts: int
    prompts: List[Any] # PromptArtifacts
    prompt_frequency_per_commit: float
    sentiment_avg: float
    efficiency: PromptEfficiencyScore
    learning_curve: LearningCurve
    top_topics: List[str]
    sentiment_summary: Dict[str, float]
    frustration_trend: List[float] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    instructional_correlations: List[InstructionalCorrelation] = field(default_factory=list)
