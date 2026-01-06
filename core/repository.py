from typing import List, Dict, Optional
from .commit import Commit
from .file_history import FileHistory

class Repository:
    """
    Represents a Git repository and its history.
    Acts as the main entry point for accessing repository data.
    """
    def __init__(self, path: str):
        """
        Initialize a Repository object.
        
        Args:
            path: Local filesystem path to the repository.
        """
        self.path = path
        self.remote_url: Optional[str] = None
        self._commits: List[Commit] = []
        self._file_histories: Dict[str, FileHistory] = {}
        
    @property
    def commits(self) -> List[Commit]:
        """Return list of commits in chronological order."""
        return self._commits
        
    @property
    def files(self) -> List[str]:
        """Return list of all filepaths found in the history."""
        return list(self._file_histories.keys())
        
    def add_commits(self, commits: List[Commit]):
        """
        Add a list of commits to the repository and update file histories.
        
        Args:
            commits: A list of Commit objects to be added to the repository's history.
        """
        # Append commits to the main list
        self._commits.extend(commits)
        
        # Sort commits by date to ensure chronological order 
        # (though usually they come ordered from extractor)
        self._commits.sort(key=lambda x: x.date if x.date else 0)
        
        # Process commits to build file histories
        for commit in commits:
            for filepath in commit.changed_files:
                if filepath not in self._file_histories:
                    self._file_histories[filepath] = FileHistory(filepath)
                
                self._file_histories[filepath].add_commit(commit)
                
    def get_file_history(self, filepath: str) -> Optional[FileHistory]:
        """
        Retrieve the historical record for a specific file path.
        
        Args:
            filepath: The relative path of the file from the repository root.
            
        Returns:
            A FileHistory instance if the file was found in the history, else None.
        """
        return self._file_histories.get(filepath)
