from fastapi import FastAPI, HTTPException
from ai_collab_analyzer.storage.database import DatabaseManager
from ai_collab_analyzer.multi_repo.aggregator import MultiRepoAggregator
from ai_collab_analyzer.benchmarking.benchmark_calculator import BenchmarkCalculator
from typing import List, Dict, Any

app = FastAPI(title="AI Collaboration Analyzer API")
db = DatabaseManager()

@app.get("/")
def read_root():
    return {"status": "online", "message": "AI Collaboration Analyzer API"}

@app.get("/repositories")
def list_repos():
    repos = db.list_repositories()
    return [{"id": r.id, "name": r.name, "path": r.path, "last_analyzed": r.last_analyzed} for r in repos]

@app.get("/repositories/{repo_name}/results")
def get_results(repo_name: str, limit: int = 10):
    results = db.get_latest_results(repo_name, limit)
    return [
        {
            "id": r.id,
            "timestamp": r.timestamp,
            "health_score": r.health_score,
            "coherence_score": r.coherence_score,
            "risk_score": r.risk_score,
            "data": r.full_data
        } 
        for r in results
    ]

@app.get("/repositories/{repo_name}/trends")
def get_trends(repo_name: str):
    results = db.get_latest_results(repo_name, limit=20)
    # Reverse to get chronological order for charts
    results.reverse()
    return {
        "dates": [r.timestamp.strftime("%Y-%m-%d %H:%M") for r in results],
        "health": [r.health_score for r in results],
        "coherence": [r.coherence_score for r in results],
        "risk": [r.risk_score for r in results]
    }

from ai_collab_analyzer.recommendations.engine import RecommendationEngine
from ai_collab_analyzer.web.api.routes.search import SearchController

@app.get("/portfolio")
def get_portfolio():
    aggregator = MultiRepoAggregator(db)
    metrics = aggregator.aggregate_portfolio()
    from dataclasses import asdict
    return asdict(metrics)

@app.get("/repositories/{repo_name}/benchmarks")
def get_benchmarks(repo_name: str):
    latest = db.get_latest_results(repo_name, limit=1)
    if not latest:
        raise HTTPException(status_code=404, detail="No analysis found")
    
    res = latest[0]
    calc = BenchmarkCalculator()
    
    benchmarks = [
        calc.calculate_benchmark('health_score', res.health_score),
        calc.calculate_benchmark('coherence_score', res.coherence_score),
        calc.calculate_benchmark('overall_risk_score', res.risk_score)
    ]
    
    from dataclasses import asdict
    return [asdict(b) for b in benchmarks]

@app.get("/repositories/{repo_name}/recommendations")
def get_recommendations(repo_name: str):
    latest = db.get_latest_results(repo_name, limit=1)
    if not latest:
        raise HTTPException(status_code=404, detail="No analysis found")
    
    engine = RecommendationEngine()
    insights = engine.generate_recommendations(latest[0].full_data)
    
    from dataclasses import asdict
    return [asdict(i) for i in insights]

@app.get("/search")
def search(query: str, category: str = "all"):
    controller = SearchController(db)
    return controller.search(query, category)

