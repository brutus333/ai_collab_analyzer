from typing import Dict, Any
from ai_collab_analyzer.models.benchmarks import BenchmarkResult

class BenchmarkCalculator:
    """
    Calculates rankings against industry averages.
    
    Using hypothetical industry baselines for Iteration 9.
    """
    
    # Baselines: {metric_name: (industry_average, standard_deviation)}
    # Lower is better for risk, higher for health/coherence
    BASELINES = {
        'health_score': (85.0, 10.0),
        'coherence_score': (75.0, 15.0),
        'overall_risk_score': (15.0, 10.0) 
    }

    def calculate_benchmark(self, metric_name: str, value: float) -> BenchmarkResult:
        if metric_name not in self.BASELINES:
            return BenchmarkResult(metric_name, value, 0, 0, "Unknown")
            
        avg, std = self.BASELINES[metric_name]
        
        # Calculate a simplified Z-score based percentile
        # Lower risk is better, higher health is better
        if metric_name == 'overall_risk_score':
            z_score = (avg - value) / std
        else:
            z_score = (value - avg) / std
            
        # Map z-score to percentile (very simplified approximation)
        percentile = 1.0 / (1.0 + pow(2.718, -z_score)) * 100
        
        rating = self._get_rating(percentile)
        
        return BenchmarkResult(
            metric_name=metric_name,
            repo_value=value,
            industry_avg=avg,
            percentile=percentile,
            rating=rating
        )

    def _get_rating(self, percentile: float) -> str:
        if percentile >= 90: return "Excellence"
        if percentile >= 70: return "Strong"
        if percentile >= 40: return "Standard"
        if percentile >= 20: return "Needs Attention"
        return "Underperforming"
