from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional

class RecommendationSeverity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

@dataclass
class ActionableInsight:
    """Represents a concrete recommendation based on analysis patterns."""
    title: str
    description: str
    severity: RecommendationSeverity
    affected_areas: List[str]
    action_item: str
    rationale: str
    category: str  # e.g., 'Architecture', 'Collaboration', 'Risk'
