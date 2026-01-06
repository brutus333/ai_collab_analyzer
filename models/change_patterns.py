from dataclasses import dataclass, field
from datetime import timedelta, datetime
from typing import List, Set, Optional
from ai_collab_analyzer.core.commit import Commit

@dataclass
class BurstPattern:
    """Captures a high-intensity sequence of commits."""
    start_commit: Commit
    following_commits: List[Commit]
    affected_files: List[str]
    duration: timedelta
    intensity_score: float

@dataclass
class Regeneration:
    """Represents a suspected AI regeneration cycle."""
    filepath: str
    commits: List[Commit]
    reason: str  # inferred reason
    count: int

@dataclass
class FixCascade:
    """Represents a commit followed by multiple fix commits."""
    initial_commit: Commit
    related_fixes: List[Commit]
    affected_files: Set[str]
    cascade_depth: int
