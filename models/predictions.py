from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime

@dataclass
class RiskFactor:
    name: str
    weight: float
    description: str

@dataclass
class FileRiskScore:
    filepath: str
    score: float  # 0 to 100
    risk_level: str  # Low, Medium, High, Critical
    factors: List[RiskFactor] = field(default_factory=list)
    trend: str = "stable"  # increasing, decreasing, stable

@dataclass
class TrendPoint:
    timestamp: datetime
    value: float

@dataclass
class Forecast:
    metric_name: str
    historical_data: List[TrendPoint]
    forecasted_data: List[TrendPoint]
    confidence_interval: float  # percentage

@dataclass
class EarlyWarning:
    severity: str  # Warning, Critical
    title: str
    message: str
    affected_files: List[str] = field(default_factory=list)

@dataclass
class PredictiveAnalysisResult:
    risk_scores: List[FileRiskScore]
    forecasts: List[Forecast]
    warnings: List[EarlyWarning]
    overall_risk_score: float
