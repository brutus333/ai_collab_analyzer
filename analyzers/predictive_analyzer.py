import os
from datetime import datetime
from typing import List, Dict, Any
from ai_collab_analyzer.analyzers.base_analyzer import BaseAnalyzer
from ai_collab_analyzer.core.repository import Repository
from ai_collab_analyzer.models.predictions import (
    PredictiveAnalysisResult, FileRiskScore, RiskFactor, Forecast, TrendPoint, EarlyWarning
)
from ai_collab_analyzer.metrics.predictive_metrics import PredictiveMetrics
from ai_collab_analyzer.metrics.basic_metrics import MetricsCalculator

class PredictiveAnalyzer(BaseAnalyzer):
    """
    Analyzes historical data to predict future risks and trends.
    """
    
    def __init__(self):
        super().__init__()
        self.metrics_calc = MetricsCalculator()
        self.predictive_calc = PredictiveMetrics()

    @property
    def name(self) -> str:
        return "Predictive Analyzer"

    @property
    def description(self) -> str:
        return "Forecasts project risks, technical debt, and file instability."

    def analyze(self, repository: Repository) -> PredictiveAnalysisResult:
        """
        Performs predictive analysis on the repository history.
        """
        risk_scores = self._calculate_all_risks(repository)
        forecasts = self._generate_forecasts(repository)
        warnings = self._generate_warnings(risk_scores)
        
        overall_risk = sum(r.score for r in risk_scores) / len(risk_scores) if risk_scores else 0.0
        
        return PredictiveAnalysisResult(
            risk_scores=risk_scores,
            forecasts=forecasts,
            warnings=warnings,
            overall_risk_score=overall_risk
        )

    def _calculate_all_risks(self, repository: Repository) -> List[FileRiskScore]:
        risk_scores = []
        
        # We'll use churn and coupling (simulated/heuristic for this iteration)
        for filepath in repository.files:
            history = repository.get_file_history(filepath)
            churn = self.metrics_calc.calculate_churn_rate(history)
            commits = history.commits
            
            # Simple acceleration: compare last 5 commits vs previous 5
            changes = [c.additions + c.deletions for c in commits]
            accel = self.predictive_calc.detect_acceleration(changes)
            
            # Heuristic frustration (dummy for now, would come from NLP results in integrated flow)
            frustration = 0.1 
            
            score = self.predictive_calc.calculate_file_risk(
                churn_rate=churn,
                coupling_count=0, # Would need CouplingAnalyzer cache
                avg_frustration=frustration,
                recent_acceleration=accel
            )
            
            level = "Low"
            if score > 80: level = "Critical"
            elif score > 60: level = "High"
            elif score > 30: level = "Medium"
            
            factors = []
            if churn > 500: factors.append(RiskFactor("High Churn", 0.4, "Large number of lines changed."))
            if accel > 0.5: factors.append(RiskFactor("Work Acceleration", 0.3, "Significant increase in recent activity."))
            
            risk_scores.append(FileRiskScore(
                filepath=filepath,
                score=score,
                risk_level=level,
                factors=factors,
                trend="increasing" if accel > 0.1 else "decreasing" if accel < -0.1 else "stable"
            ))
            
        return sorted(risk_scores, key=lambda x: x.score, reverse=True)

    def _generate_forecasts(self, repository: Repository) -> List[Forecast]:
        # Forecast total churn growth
        commits_by_date = {}
        for c in sorted(repository.commits, key=lambda x: x.date):
            d = c.date.date()
            commits_by_date[d] = commits_by_date.get(d, 0) + (c.additions + c.deletions)
            
        dates = sorted(commits_by_date.keys())
        if len(dates) < 2:
            return []
            
        historical = []
        cumulative = 0
        for d in dates:
            cumulative += commits_by_date[d]
            historical.append((datetime.combine(d, datetime.min.time()), float(cumulative)))
            
        future_points = self.predictive_calc.forecast_linear(historical)
        
        return [Forecast(
            metric_name="Cumulative Churn",
            historical_data=[TrendPoint(p[0], p[1]) for p in historical],
            forecasted_data=[TrendPoint(p[0], p[1]) for p in future_points],
            confidence_interval=0.85
        )]

    def _generate_warnings(self, risk_scores: List[FileRiskScore]) -> List[EarlyWarning]:
        warnings = []
        critical_files = [r.filepath for r in risk_scores if r.risk_level == "Critical"]
        
        if critical_files:
            warnings.append(EarlyWarning(
                severity="Critical",
                title="Imminent Instability Detected",
                message=f"The following files have extreme churn and acceleration: {', '.join(critical_files[:3])}",
                affected_files=critical_files
            ))
            
        return warnings
