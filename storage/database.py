from ai_collab_analyzer.storage.models import init_db, get_session, RepositoryRecord, AnalysisResultRecord
from datetime import datetime
import json

class DatabaseManager:
    def __init__(self, db_url="sqlite:///ai_collab.db"):
        self.engine = init_db(db_url)
        self.session = get_session(self.engine)

    def save_analysis(self, repo_name: str, repo_path: str, result: dict):
        # Find or create repository
        repo = self.session.query(RepositoryRecord).filter_by(name=repo_name).first()
        if not repo:
            repo = RepositoryRecord(name=repo_name, path=repo_path)
            self.session.add(repo)
            self.session.commit()

        # Create analysis record
        # Note: We strip some non-serializable objects if needed, 
        # but our results should be serializable by now (or converted to JSON-friendly format)
        
        # Extract top-level metrics for quick query
        health = result.get('health_score', 0)
        coherence = result.get('coherence_score', 0)
        risk = result.get('overall_risk_score', 0)
        
        # For the full_data, ensure we don't store custom objects that can't be JSONified
        # (Though SQLAlchemy JSON column should handle dicts)
        
        analysis_record = AnalysisResultRecord(
            repo_id=repo.id,
            timestamp=datetime.utcnow(),
            health_score=health,
            coherence_score=coherence,
            risk_score=risk,
            full_data=result
        )
        
        repo.last_analyzed = datetime.utcnow()
        self.session.add(analysis_record)
        self.session.commit()
        return analysis_record.id

    def get_latest_results(self, repo_name: str, limit: int = 5):
        repo = self.session.query(RepositoryRecord).filter_by(name=repo_name).first()
        if not repo:
            return []
        
        return self.session.query(AnalysisResultRecord)\
            .filter_by(repo_id=repo.id)\
            .order_by(AnalysisResultRecord.timestamp.desc())\
            .limit(limit).all()

    def list_repositories(self):
        return self.session.query(RepositoryRecord).all()
