from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum

class Severity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class CodeLocation:
    filepath: str
    line_start: int
    line_end: int
    entity_name: Optional[str] = None

@dataclass
class Finding:
    title: str
    description: str
    severity: Severity
    location: Optional[CodeLocation] = None
    recommendation: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DimensionScore:
    name: str
    score: float  # 0 to 100
    weight: float
    details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PerspectiveResult:
    perspective_name: str
    score: float
    dimensions: List[DimensionScore]
    findings: List[Finding]
    recommendations: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CodeEntity:
    filepath: str
    content: str
    type: str = "file"  # file, function, class
    ast_tree: Optional[Any] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MultiPerspectiveResult:
    aggregate_scores: Dict[str, float]
    perspective_results: List[PerspectiveResult]
    composite_score: float
    critical_findings: List[Finding]
    file_breakdown: Dict[str, Dict[str, float]] = field(default_factory=dict)
