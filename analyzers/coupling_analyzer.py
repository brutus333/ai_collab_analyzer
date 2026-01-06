from typing import Dict, Any, List
import itertools
import networkx as nx
from ai_collab_analyzer.analyzers.base_analyzer import BaseAnalyzer
from ai_collab_analyzer.core.repository import Repository

class CouplingAnalyzer(BaseAnalyzer):
    """
    Analyzes temporal coupling between files.
    """
    
    @property
    def name(self) -> str:
        return "Coupling Analyzer"
        
    @property
    def description(self) -> str:
        return "Identifies files that frequently change together."
        
    def analyze(self, repository: Repository) -> Dict[str, Any]:
        """
        Build a coupling graph and return edges.
        """
        graph = nx.Graph()
        
        # Count co-occurrences
        pair_counts = {}
        
        for commit in repository.commits:
            files = list(set(commit.changed_files)) # unique files in commit
            if len(files) < 2:
                continue
                
            # Create pairs
            for f1, f2 in itertools.combinations(files, 2):
                pair = tuple(sorted((f1, f2)))
                pair_counts[pair] = pair_counts.get(pair, 0) + 1
                
        # Build graph
        for pair, count in pair_counts.items():
            # Filter low coupling? Let's say at least 1 for now (raw)
            # logic for normalization could be added (Jaccard)
            graph.add_edge(pair[0], pair[1], weight=count)
            
        # Extract edges for serialization
        edges = []
        for u, v, data in graph.edges(data=True):
            edges.append({
                "source": u,
                "target": v,
                "weight": data["weight"]
            })
            
        # Sort by weight desc
        edges.sort(key=lambda x: x["weight"], reverse=True)
            
        return {
            "coupling_edges": edges,
            "node_count": graph.number_of_nodes(),
            "edge_count": graph.number_of_edges()
        }
