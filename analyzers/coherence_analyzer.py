import os
from typing import List, Dict, Any
from ai_collab_analyzer.analyzers.base_analyzer import BaseAnalyzer
from ai_collab_analyzer.core.repository import Repository
from ai_collab_analyzer.parsers.language_detector import LanguageDetector
from ai_collab_analyzer.parsers.ast_parser import PythonASTParser
from ai_collab_analyzer.similarity.code_similarity import CodeSimilarityAnalyzer
from ai_collab_analyzer.similarity.pattern_matcher import PatternMatcher
from ai_collab_analyzer.models.coherence import CoherenceAnalysisResult, DuplicationCluster, DriftEvent

class CoherenceAnalyzer(BaseAnalyzer):
    """
    Analyzes code coherence, consistency, and drift.
    """
    
    def __init__(self, similarity_threshold: float = 85.0):
        super().__init__()
        self.similarity_threshold = similarity_threshold
        self.python_parser = PythonASTParser()
        self.similarity_analyzer = CodeSimilarityAnalyzer(threshold=similarity_threshold)
        self.pattern_matcher = PatternMatcher()

    @property
    def name(self) -> str:
        return "Coherence Analyzer"

    @property
    def description(self) -> str:
        return "Analyzes structural consistency and detects code duplication."

    def analyze(self, repository: Repository) -> CoherenceAnalysisResult:
        """
        Performs coherence analysis on the repository.
        """
        all_nodes = []
        repo_path = repository.path
        
        # 1. Extract nodes from all supported files
        for root, _, files in os.walk(repo_path):
            for file in files:
                filepath = os.path.join(root, file)
                if LanguageDetector.detect_language(filepath) == "python":
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            code = f.read()
                            nodes = self.python_parser.parse(code)
                            for node in nodes:
                                # Keep track of where this node came from
                                node.filepath = os.path.relpath(filepath, repo_path)
                                all_nodes.append(node)
                    except Exception:
                        continue

        # 2. Find near-duplicates
        blocks = [(f"{n.filepath}:{n.name}", n.body) for n in all_nodes]
        duplicates = self.similarity_analyzer.find_near_duplicates(blocks)
        
        clusters = []
        processed_pairs = set()
        
        for id1, id2, score in duplicates:
            # Simple clustering: each pair is a starting point for a cluster
            # For this iteration, we keep it simple: one cluster per near-duplicate pair found
            # that's not already covered.
            if (id1, id2) in processed_pairs:
                continue
                
            # Find the original node for the snippet
            snippet = ""
            for n in all_nodes:
                if f"{n.filepath}:{n.name}" == id1:
                    snippet = n.body
                    break
            
            clusters.append(DuplicationCluster(
                cluster_id=f"cluster_{len(clusters)}",
                files=[id1.split(':')[0], id2.split(':')[0]],
                similarity_score=score,
                code_snippet=snippet[:200] + "...",
                recommendation="Consider extracting common logic into a shared utility."
            ))
            processed_pairs.add((id1, id2))
            processed_pairs.add((id2, id1))

        # 3. Calculate Coherence Score
        # A simple starting formula: 100 - (number of duplication clusters * 5)
        # Cap it at 0-100.
        coherence_score = max(0, 100 - (len(clusters) * 5))
        
        return CoherenceAnalysisResult(
            coherence_score=float(coherence_score),
            duplication_clusters=clusters,
            summary=f"Detected {len(clusters)} duplication clusters."
        )
