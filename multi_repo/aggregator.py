from typing import List, Dict, Any
from ai_collab_analyzer.models.benchmarks import PortfolioMetrics
from ai_collab_analyzer.storage.database import DatabaseManager

class MultiRepoAggregator:
    """
    Aggregates metrics across multiple repositories to provide portfolio insights.
    """
    def __init__(self, db: DatabaseManager):
        self.db = db

    def aggregate_portfolio(self) -> PortfolioMetrics:
        repos = self.db.list_repositories()
        if not repos:
            return PortfolioMetrics(0, 0, 0, 0)

        total_health = 0
        total_coherence = 0
        total_risk = 0
        all_risky_files = []
        comparisons = []

        active_repos = 0
        for repo in repos:
            latest = self.db.get_latest_results(repo.name, limit=1)
            if not latest:
                continue
            
            res = latest[0]
            active_repos += 1
            total_health += res.health_score or 0
            total_coherence += res.coherence_score or 0
            total_risk += res.risk_score or 0
            
            # Collect risky files from this repo
            repo_data = res.full_data
            risk_scores = repo_data.get('risk_scores', {})
            
            # risk_scores might be a dict {file: score} or a list if it was a custom object
            if isinstance(risk_scores, dict):
                for filepath, score in risk_scores.items():
                    all_risky_files.append({
                        'repo': repo.name,
                        'file': filepath,
                        'risk_score': score
                    })
            elif isinstance(risk_scores, list):
                # If it's a list, it might be a list of dicts or records
                for item in risk_scores:
                    if isinstance(item, dict):
                        # Try to find file and score keys
                        f = item.get('file') or item.get('filepath')
                        s = item.get('risk_score') or item.get('score')
                        if f and s:
                            all_risky_files.append({'repo': repo.name, 'file': f, 'risk_score': s})
            
            comparisons.append({
                'name': repo.name,
                'health': res.health_score,
                'coherence': res.coherence_score,
                'risk': res.risk_score
            })

        if active_repos == 0:
            return PortfolioMetrics(0, 0, 0, 0)

        # Sort all risky files across portfolio
        all_risky_files.sort(key=lambda x: x['risk_score'], reverse=True)

        return PortfolioMetrics(
            total_repos=active_repos,
            avg_health_score=total_health / active_repos,
            avg_coherence_score=total_coherence / active_repos,
            avg_risk_score=total_risk / active_repos,
            top_risky_files=all_risky_files[:10],
            repo_comparisons=comparisons
        )
