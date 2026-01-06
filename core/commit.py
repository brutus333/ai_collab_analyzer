from datetime import datetime
from typing import List, Dict, Any, Optional

class Commit:
    """
    Represents a single Git commit with its metadata and changes.
    """
    def __init__(self, commit_data: Dict[str, Any]):
        """
        Initialize a Commit object.
        
        Args:
            commit_data: Dictionary containing commit information.
                         Keys expected: hash, author_name, author_email, author_date, 
                         msg, files, insertions, deletions, lines, merge
        """
        self._data = commit_data
        
    @property
    def hash(self) -> Optional[str]:
        return self._data.get("hash")
        
    @property
    def author(self) -> Optional[str]:
        return self._data.get("author_name")
        
    @property
    def email(self) -> Optional[str]:
        return self._data.get("author_email")
        
    @property
    def date(self) -> Optional[datetime]:
        return self._data.get("author_date")
        
    @property
    def message(self) -> Optional[str]:
        return self._data.get("msg")
    
    @property
    def changed_files(self) -> List[str]:
        return self._data.get("files", [])
        
    @property
    def additions(self) -> int:
        return self._data.get("insertions", 0)
        
    @property
    def deletions(self) -> int:
        return self._data.get("deletions", 0)
        
    @property
    def total_changes(self) -> int:
        return self._data.get("lines", 0)
        
    @property
    def instructional_changes(self) -> List[str]:
        """Returns lines identified as agentic instructions added in this commit."""
        return self._data.get("instructional_changes", [])

    def is_merge(self) -> bool:
        """Return True if this is a merge commit."""
        return self._data.get("merge", False)
        
    def get_size(self) -> int:
        """Return the size of the commit (total lines changed)."""
        return self.total_changes
