from typing import List, Dict, Tuple
from datetime import date
from collections import defaultdict
from ai_collab_analyzer.core.repository import Repository
from ai_collab_analyzer.core.file_history import FileHistory
from ai_collab_analyzer.core.commit import Commit
from ai_collab_analyzer.analyzers.fix_detector import FixDetector

class MetricsCalculator:
    """
    Calculates various metrics for repository analysis.
    """
    
    def calculate_fix_ratio(self, commits: List[Commit]) -> float:
        """
        Calculate the ratio of fix commits to total commits.
        """
        if not commits:
            return 0.0
            
        detector = FixDetector()
        fix_count = sum(1 for c in commits if detector.is_fix_commit(c))
        
        return fix_count / len(commits)

    def calculate_churn_rate(self, file_history: FileHistory) -> float:
        """
        Calculate churn rate for a file.
        Returns average lines changed per commit.
        """
        return file_history.get_churn_rate()

    def calculate_commit_frequency(self, commits: List[Commit], period: str = "D") -> Dict[date, int]:
        """
        Calculate commit frequency over time.
        
        Args:
            commits: List of commits to analyze
            period: Aggregation period ('D' for day). Currently only supports daily.
            
        Returns:
            Dictionary mapping date to commit count.
        """
        freq_map = defaultdict(int)
        
        for commit in commits:
            if commit.date:
                # Truncate to day
                day = commit.date.date()
                freq_map[day] += 1
                
        return dict(freq_map)

    def calculate_file_hotspots(self, repository: Repository, top_n: int = 10) -> List[Tuple[str, int]]:
        """
        Identify file hotspots based on change frequency (number of commits).
        
        Args:
            repository: Repository to analyze
            top_n: Number of top hotspots to return
            
        Returns:
            List of tuples (filepath, commit_count) sorted by count descending.
        """
        hotspots = []
        
        for filepath in repository.files:
            history = repository.get_file_history(filepath)
            if history:
                # Using change frequency (commit count) as the primary hotspot metric
                # Could also mix in churn rate
                count = int(history.get_change_frequency())
                hotspots.append((filepath, count))
                
        # Sort by count descending
        hotspots.sort(key=lambda x: x[1], reverse=True)
        
        return hotspots[:top_n]
