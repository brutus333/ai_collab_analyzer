from typing import List, Dict, Any
from ai_collab_analyzer.storage.database import DatabaseManager

class RepositoryComparator:
    """
    Compares two or more repositories.
    """
    def __init__(self, db: DatabaseManager):
        self.db = db

    def compare(self, repo_names: List[str]) -> Dict[str, Any]:
        results = []
        for name in repo_names:
            latest = self.db.get_latest_results(name, limit=1)
            if latest:
                res = latest[0]
                results.append({
                    'name': name,
                    'health': res.health_score,
                    'coherence': res.coherence_score,
                    'risk': res.risk_score,
                    'timestamp': res.timestamp.isoformat()
                })

        # Identify strengths and weaknesses
        insights = []
        if len(results) >= 2:
            # Sort by health
            sorted_health = sorted(results, key=lambda x: x['health'], reverse=True)
            insights.append(f"Champion in Health: {sorted_health[0]['name']} ({sorted_health[0]['health']:.1f})")
            
            # Sort by risk (lower is better)
            sorted_risk = sorted(results, key=lambda x: x['risk'])
            insights.append(f"Lowest Risk Project: {sorted_risk[0]['name']} ({sorted_risk[0]['risk']:.2f})")

        return {
            'comparison': results,
            'insights': insights
        }
