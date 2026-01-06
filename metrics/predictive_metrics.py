import numpy as np
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta

class PredictiveMetrics:
    """
    Heuristics and statistical methods for project forecasting.
    """
    
    @staticmethod
    def calculate_file_risk(
        churn_rate: float,
        coupling_count: int,
        avg_frustration: float,
        recent_acceleration: float
    ) -> float:
        """
        Calculates a risk score from 0 to 100.
        """
        # Weights
        # Churn: 30%, Coupling: 30%, Frustration: 20%, Acceleration: 20%
        score = (
            min(1.0, churn_rate / 1000) * 30 +
            min(1.0, coupling_count / 10) * 30 +
            avg_frustration * 20 +
            min(1.0, recent_acceleration) * 20
        )
        return min(100.0, score)

    @staticmethod
    def forecast_linear(data: List[Tuple[datetime, float]], next_periods: int = 5) -> List[Tuple[datetime, float]]:
        """
        Performs a simple linear regression to forecast future points.
        """
        if len(data) < 2:
            return []
            
        # Convert dates to numerical values (ordinal)
        x = np.array([d[0].toordinal() for d in data])
        y = np.array([d[1] for d in data])
        
        # Linear fit (y = mx + b)
        m, b = np.polyfit(x, y, 1)
        
        last_date = data[-1][0]
        forecast = []
        for i in range(1, next_periods + 1):
            future_date = last_date + timedelta(days=i * 7) # Weekly increments
            future_val = m * future_date.toordinal() + b
            forecast.append((future_date, max(0.0, float(future_val))))
            
        return forecast

    @staticmethod
    def detect_acceleration(values: List[float], window: int = 3) -> float:
        """
        Calculates the change in growth rate (acceleration).
        """
        if len(values) < window * 2:
            return 0.0
            
        recent = sum(values[-window:]) / window
        previous = sum(values[-2*window:-window]) / window
        
        if previous == 0:
            return 1.0 if recent > 0 else 0.0
            
        return (recent - previous) / previous
