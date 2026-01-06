from typing import List, Dict, Any, Tuple
from ai_collab_analyzer.core.repository import Repository
from ai_collab_analyzer.extractors.prompt_extractor import PromptExtractor, PromptArtifact
from ai_collab_analyzer.analyzers.base_analyzer import BaseAnalyzer
from ai_collab_analyzer.nlp.message_analyzer import MessageAnalyzer, Intent
from ai_collab_analyzer.nlp.sentiment_analyzer import SentimentAnalyzer
from ai_collab_analyzer.nlp.topic_extractor import TopicExtractor
from ai_collab_analyzer.models.prompt_insights import PromptInsightResult, PromptEfficiencyScore, LearningCurve, InstructionalCorrelation

class PromptAnalyzer(BaseAnalyzer):
    """
    Analyzes the repository for prompt engineering artifacts and collaboration insights.
    """
    
    def __init__(self):
        super().__init__()
        self.extractor = PromptExtractor()
        self.message_analyzer = MessageAnalyzer()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.topic_extractor = TopicExtractor()
        
    @property
    def name(self) -> str:
        return "Prompt Analyzer"

    @property
    def description(self) -> str:
        return "Extracts AI prompts and analyzes developer intent, sentiment, and efficiency."
        
    def analyze(self, repository: Repository) -> PromptInsightResult:
        """
        Perform the expanded prompt analysis.
        """
        all_prompts = self._scan_current_files(repository)
        commit_prompts = self._scan_commit_messages(repository)
        combined_prompts = all_prompts + commit_prompts
        
        # 1. NLP Analysis of Commits
        messages = [c.message for c in repository.commits]
        sentiments = self.sentiment_analyzer.track_sentiment_trend(messages)
        intents = [self.message_analyzer.classify_intent(m) for m in messages]
        frustration_scores = [self.message_analyzer.detect_frustration(m) for m in messages]
        
        # 2. Extract Topics
        topics = self.topic_extractor.extract_topics(messages)
        
        # 3. Calculate Efficiency & Learning Curve
        feature_commits = [i for i, intent in enumerate(intents) if intent == Intent.FEATURE_ADD]
        success_count = 0
        revisions = []
        
        for idx in feature_commits:
            # Success = Feature add NOT followed by Bug Fix
            if idx + 1 < len(intents) and intents[idx+1] == Intent.BUG_FIX:
                revisions.append(1)
                continue
            success_count += 1
            revisions.append(0)
            
        success_rate = (success_count / len(feature_commits) * 100) if feature_commits else 100.0
        avg_revisions = sum(revisions)/len(revisions) if revisions else 0
        
        efficiency = PromptEfficiencyScore(
            overall_score=success_rate,
            first_time_success_rate=success_rate,
            avg_revisions_per_feature=avg_revisions
        )
        
        # Learning Curve: Trend of success over time
        window_size = max(1, len(revisions) // 5)
        efficiency_trend = []
        for i in range(0, len(revisions), window_size):
            window = revisions[i:i+window_size]
            win_success = (window.count(0) / len(window) * 100) if window else 100
            efficiency_trend.append(win_success)
        
        improvement = (efficiency_trend[-1] - efficiency_trend[0]) if len(efficiency_trend) > 1 else 0
        skill_level = "Intermediate" if success_rate > 70 else "Beginner"
        if success_rate > 90 and improvement > 0: skill_level = "Advanced"

        learning = LearningCurve(
            improvement_rate=improvement,
            skill_level=skill_level,
            plateau_detected=improvement < 5 and len(efficiency_trend) > 3,
            efficiency_trend=efficiency_trend
        )

        # 4. Instructional Correlation
        correlations = self._calculate_instructional_correlations(repository, intents)
        
        return PromptInsightResult(
            total_prompts=len(combined_prompts),
            prompts=combined_prompts,
            prompt_frequency_per_commit=len(combined_prompts) / len(repository.commits) if repository.commits else 0,
            sentiment_avg=sum(sentiments) / len(sentiments) if sentiments else 0,
            efficiency=efficiency,
            learning_curve=learning,
            top_topics=[t[0] for t in topics],
            sentiment_summary={"average": sum(sentiments)/len(sentiments) if sentiments else 0},
            frustration_trend=frustration_scores,
            instructional_correlations=correlations
        )
        
    def _calculate_instructional_correlations(self, repository: Repository, intents: List[Intent]) -> List[InstructionalCorrelation]:
        """
        Identify commits that introduced instructions and measure impact on subsequent code quality.
        """
        correlations = []
        window = 15 # Look at 15 commits before/after
        
        for i, commit in enumerate(repository.commits):
            if commit.instructional_changes:
                # Calculate efficiency BEFORE this commit
                eff_before = self._get_efficiency_in_range(intents, max(0, i - window), i)
                # Calculate efficiency AFTER this commit
                eff_after = self._get_efficiency_in_range(intents, i + 1, min(len(intents), i + 1 + window))
                
                impact = eff_after - eff_before
                
                for instr in commit.instructional_changes[:3]: # Limit to top 3 snippets per commit
                    context = "Improved" if impact > 0 else "Reduced"
                    score_abs = abs(impact)
                    correlations.append(InstructionalCorrelation(
                        instruction=instr,
                        impact_score=impact,
                        context=f"{context} first-time success rate by {score_abs:.1f}%",
                        commit_hash=str(commit.hash)[:7]
                    ))
        
        # Sort by impact score descending
        correlations.sort(key=lambda x: x.impact_score, reverse=True)
        return correlations[:10] # Return top 10 most impactful rules

    def _get_efficiency_in_range(self, intents: List[Intent], start: int, end: int) -> float:
        """Calculate success rate (% features not needing immediate fix) in a range."""
        slice_intents = intents[start:end]
        if not slice_intents: return 0.0
        
        features = 0
        successes = 0
        for i in range(len(slice_intents)):
            if slice_intents[i] == Intent.FEATURE_ADD:
                features += 1
                # Check next in the GLOBAL intents if possible, or just in slice
                next_idx = start + i + 1
                if next_idx < len(intents) and intents[next_idx] != Intent.BUG_FIX:
                    successes += 1
                elif next_idx >= len(intents):
                    successes += 1 # Assume success if it's the end
                    
        return (successes / features * 100) if features > 0 else 100.0

    def _scan_current_files(self, repository: Repository) -> List[PromptArtifact]:
        """
        Scans the current version of all text files in the repo.
        """
        prompts = []
        import os
        
        # Iterate over known files in history
        for filepath in repository.files:
            try:
                # Construct full path
                full_path = os.path.join(repository.path, filepath)
                
                if os.path.exists(full_path) and os.path.isfile(full_path):
                     with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        # Pass relative path to extractor for reporting
                        file_prompts = self.extractor.extract_from_content(content, filepath)
                        prompts.extend(file_prompts)
            except Exception:
                continue 
        return prompts

    def _scan_commit_messages(self, repository: Repository) -> List[PromptArtifact]:
        """
        Scans all commit messages.
        """
        prompts = []
        for commit in repository.commits:
            prompt = self.extractor.extract_from_commit_message(commit.message)
            if prompt:
                # Enrich with commit info
                prompt.filepath = str(commit.hash)[:7] # Use hash as ID
                prompts.append(prompt)
        return prompts
