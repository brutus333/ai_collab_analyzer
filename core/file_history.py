from typing import List, Optional
from datetime import datetime
from .commit import Commit

class FileHistory:
    """
    Tracks the history of a single file across commits.
    """
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.commits: List[Commit] = []
        self._total_changes = 0
        self._creation_date: Optional[datetime] = None
        self._last_modified: Optional[datetime] = None
        
    def add_commit(self, commit: Commit):
        """
        Add a commit to this file's history.
        Assumes commits are added in chronological order.
        """
        self.commits.append(commit)
        
        # In a real scenario, we'd need to parse per-file changes from the commit.
        # For this iteration, we might assume the commit object *only* contains changes for this file 
        # OR we rely on the commit to provide file-specific stats if possible.
        # However, the Commit object currently stores total stats for the commit, not per file.
        # Detailed per-file stats usually come from the diff.
        # For now, we will use a simplified approach: 
        # If the commit has metric data, we might need to approximate or update Commit 
        # to support file-specific metrics if available.
        
        # Note: The design in SW Architecture implies FileHistory tracks the file.
        # We will accumulate 'total_changes' from the commit if it's the only file,
        # or we might need to refine the Commit model later.
        # For Iteration 1, we will assume the Commit object passed here IS relevant to this file.
        # But `commit.total_changes` is for the WHOLE commit.
        # Ideally, we should receive file-specific change count.
        
        # Let's check `test_file_history.py`. It initializes Commit with `lines=10` etc.
        # So we can use `commit.total_changes` as a proxy for now, 
        # or better yet, verify if we should change the API.
        
        # Using commit.total_changes as per current Commit implementation 
        # (which wraps dictionary that might come from pydriller's modified_file object in practice)
        
        self._total_changes += commit.total_changes
        
        if self._creation_date is None:
            self._creation_date = commit.date
            
        if self._last_modified is None or (commit.date and commit.date > self._last_modified):
            self._last_modified = commit.date

    @property
    def total_changes(self) -> int:
        return self._total_changes

    @property
    def creation_date(self) -> Optional[datetime]:
        return self._creation_date

    @property
    def last_modified(self) -> Optional[datetime]:
        """Return the date of the most recent commit to this file."""
        return self._last_modified

    def get_churn_rate(self) -> float:
        """
        Calculate churn rate (average lines changed per commit).
        
        Returns:
            Mean number of lines added/deleted per modification event.
        """
        if not self.commits:
            return 0.0
        return self._total_changes / len(self.commits)

    def get_change_frequency(self) -> float:
        """
        Calculate change frequency (total commit count).
        
        Returns:
            The number of commits that have modified this file.
        """
        return float(len(self.commits))
