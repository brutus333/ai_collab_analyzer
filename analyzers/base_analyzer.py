from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from ai_collab_analyzer.core.repository import Repository

class BaseAnalyzer(ABC):
    """
    Abstract base class for all repository analyzers.
    """
    
    def __init__(self):
        self._cache = {}
    
    @abstractmethod
    def analyze(self, repository: Repository) -> Any:
        """
        Perform analysis on the repository.
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """
        Name of the analyzer.
        """
        pass
        
    @property
    @abstractmethod
    def description(self) -> str:
        """
        Description of what the analyzer does.
        """
        pass
        
    def cache_result(self, key: str, value: Any):
        """
        Cache an intermediate result.
        """
        self._cache[key] = value
        
    def get_cached_result(self, key: str) -> Optional[Any]:
        """
        Retrieve a cached result.
        """
        return self._cache.get(key)
