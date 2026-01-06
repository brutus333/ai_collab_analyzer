from typing import List, Dict, Any, Optional
from datetime import timedelta, datetime
from ai_collab_analyzer.analyzers.base_analyzer import BaseAnalyzer
from ai_collab_analyzer.core.repository import Repository
from ai_collab_analyzer.core.commit import Commit
from ai_collab_analyzer.core.file_history import FileHistory
from ai_collab_analyzer.models.change_patterns import BurstPattern, Regeneration

class PatternAnalyzer(BaseAnalyzer):
    """
    Analyzes temporal patterns in the repository history.
    """
    
    @property
    def name(self) -> str:
        return "Change Pattern Analyzer"
        
    @property
    def description(self) -> str:
        return "Detects burst patterns, regenerations, and stability timelines."
        
    def analyze(self, repository: Repository) -> Dict[str, Any]:
        """
        Perform pattern analysis.
        """
        bursts = self.detect_burst_patterns(repository.commits)
        
        regenerations = []
        for filepath in repository.files:
            history = repository.get_file_history(filepath)
            if history:
                regenerations.extend(self.detect_regenerations(history))
                
        return {
            "burst_patterns_count": len(bursts),
            "regeneration_cycles_count": len(regenerations),
            "bursts": bursts, # Objects, likely need serialization for report
            "regenerations": regenerations
        }

    def detect_burst_patterns(self, commits: List[Commit], threshold_minutes: int = 60) -> List[BurstPattern]:
        """
        Identify sequences of commits that happen in short succession.
        """
        if not commits:
            return []
            
        bursts = []
        threshold = timedelta(minutes=threshold_minutes)
        
        current_burst_start: Optional[Commit] = None
        current_burst_commits: List[Commit] = []
        
        sorted_commits = sorted(commits, key=lambda c: c.date if c.date else datetime.min)
        
        for i, commit in enumerate(sorted_commits):
            if not commit.date:
                continue
                
            if current_burst_start is None:
                current_burst_start = commit
                continue
                
            time_diff = commit.date - sorted_commits[i-1].date
            
            if time_diff <= threshold:
                current_burst_commits.append(commit)
            else:
                # End of a potential burst
                if current_burst_commits:
                    # Minimum 2 related commits (start + at least 1 following)
                    duration = sorted_commits[i-1].date - current_burst_start.date
                    
                    # Extract affected files
                    affected = set()
                    affected.update(current_burst_start.changed_files)
                    for c in current_burst_commits:
                        affected.update(c.changed_files)
                        
                    bursts.append(BurstPattern(
                        start_commit=current_burst_start,
                        following_commits=list(current_burst_commits),
                        affected_files=list(affected),
                        duration=duration,
                        intensity_score=float(len(current_burst_commits))
                    ))
                
                # Reset
                current_burst_start = commit
                current_burst_commits = []
                
        # Check final burst
        if current_burst_start and current_burst_commits:
            duration = current_burst_commits[-1].date - current_burst_start.date
            affected = set()
            affected.update(current_burst_start.changed_files)
            for c in current_burst_commits:
                affected.update(c.changed_files)
                
            bursts.append(BurstPattern(
                start_commit=current_burst_start,
                following_commits=list(current_burst_commits),
                affected_files=list(affected),
                duration=duration,
                intensity_score=float(len(current_burst_commits))
            ))
            
        return bursts

    def detect_regenerations(self, file_history: FileHistory, time_threshold_minutes: int = 15) -> List[Regeneration]:
        """
        Detect potential regeneration cycles for a file.
        Heuristic: High frequency changes (short intervals) with significant churn.
        """
        if len(file_history.commits) < 3:
            return []
            
        regenerations = []
        threshold = timedelta(minutes=time_threshold_minutes)
        
        # We look for a window of at least 3 commits close together
        
        window = []
        
        for commit in file_history.commits:
            if not window:
                window.append(commit)
                continue
                
            if not commit.date or not window[-1].date:
                continue
                
            diff = commit.date - window[-1].date
            
            if diff <= threshold:
                window.append(commit)
            else:
                # Analyze window
                if len(window) >= 3:
                    # Check for churn? For now pure frequency
                    regenerations.append(Regeneration(
                        filepath=file_history.filepath,
                        commits=list(window),
                        reason="High frequency updates",
                        count=len(window)
                    ))
                window = [commit]
                
        if len(window) >= 3:
             regenerations.append(Regeneration(
                filepath=file_history.filepath,
                commits=list(window),
                reason="High frequency updates",
                count=len(window)
            ))
            
        return regenerations
