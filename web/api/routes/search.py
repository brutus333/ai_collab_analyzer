from typing import List, Dict, Any
from ai_collab_analyzer.storage.database import DatabaseManager

class SearchController:
    """
    Handles global searching across commits, prompts, and files.
    """
    def __init__(self, db: DatabaseManager):
        self.db = db

    def search(self, query: str, category: str = 'all') -> List[Dict[str, Any]]:
        results = []
        repos = self.db.list_repositories()
        query = query.lower()

        for repo in repos:
            latest = self.db.get_latest_results(repo.name, limit=1)
            if not latest:
                continue
            
            data = latest[0].full_data
            
            # Search Prompts
            if category in ['all', 'prompt']:
                prompts = data.get('prompts', [])
                for p in prompts:
                    content = p.get('content', '').lower()
                    if query in content:
                        results.append({
                            'repo': repo.name,
                            'type': 'Prompt',
                            'match': content[:100] + "...",
                            'meta': p.get('author', 'Unknown')
                        })

            # Search Commits
            if category in ['all', 'commit']:
                patterns = data.get('patterns', [])
                for pat in patterns:
                    msg = pat.get('message', '').lower()
                    if query in msg:
                        results.append({
                            'repo': repo.name,
                            'type': 'Commit',
                            'match': msg,
                            'meta': pat.get('author', 'Unknown')
                        })
            
            # Search Files
            if category in ['all', 'file']:
                files = data.get('risk_scores', {})
                if isinstance(files, dict):
                    for f, score in files.items():
                        if query in f.lower():
                            results.append({
                                'repo': repo.name,
                                'type': 'File',
                                'match': f,
                                'meta': f"Risk: {score:.1f}"
                            })
                elif isinstance(files, list):
                    for item in files:
                        if isinstance(item, dict):
                            f = item.get('file') or item.get('filepath')
                            score = item.get('risk_score') or item.get('score') or item.get('risk') or 0
                            if f and query in f.lower():
                                results.append({
                                    'repo': repo.name,
                                    'type': 'File',
                                    'match': f,
                                    'meta': f"Risk: {score:.1f}"
                                })

        return results
