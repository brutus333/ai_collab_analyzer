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
    
    def __init__(self, similarity_threshold: float = 90.0):
        super().__init__()
        self.similarity_threshold = similarity_threshold
        self.python_parser = PythonASTParser()
        # Increased default threshold to 90% and added min_length to CodeSimilarityAnalyzer
        self.similarity_analyzer = CodeSimilarityAnalyzer(threshold=similarity_threshold, min_length=100)
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
                                
                                # Filtering: Ignore trivial/very small functions (boilerplate/getters)
                                if len(node.body.splitlines()) < 6:
                                    continue
                                    
                                all_nodes.append(node)
                    except Exception:
                        continue

        # 2. Find near-duplicates
        # Optimization: Map IDs to bodies once to avoid O(n) lookup inside the loop
        node_lookup = {f"{n.filepath}:{n.name}": n.body for n in all_nodes}
        blocks = [(id, body) for id, body in node_lookup.items()]
        duplicates = self.similarity_analyzer.find_near_duplicates(blocks)
        
        clusters = []
        processed_pairs = set()
        duplicated_ids = set()
        
        for id1, id2, score in duplicates:
            if (id1, id2) in processed_pairs:
                continue
                
            snippet = node_lookup.get(id1, "")
            
            clusters.append(DuplicationCluster(
                cluster_id=f"cluster_{len(clusters)}",
                files=[id1.split(':')[0], id2.split(':')[0]],
                similarity_score=score,
                code_snippet=snippet[:200] + "...",
                recommendation="Consider extracting common logic into a shared utility or base class."
            ))
            processed_pairs.add((id1, id2))
            processed_pairs.add((id2, id1))
            duplicated_ids.add(id1)
            duplicated_ids.add(id2)

        # 3. Calculate Coherence Score
        # Formula: 100 * (1 - (duplicated_nodes / total_nodes))
        # This provides a more proportional penalty than a fixed deduction per cluster.
        total_nodes_count = len(all_nodes)
        if total_nodes_count > 0:
            dup_ratio = len(duplicated_ids) / total_nodes_count
            # We weight the penalty: if 20% of nodes are duplicated, score is 80%
            # If 50% are duplicated, score is 50%
            coherence_score = 100.0 * (1.0 - dup_ratio)
        else:
            coherence_score = 100.0
            
        return CoherenceAnalysisResult(
            coherence_score=float(coherence_score),
            duplication_clusters=clusters,
            summary=f"Analyzed {total_nodes_count} significant code blocks. Detected {len(clusters)} clusters involving {len(duplicated_ids)} nodes."
        )
