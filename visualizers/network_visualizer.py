import networkx as nx
import plotly.graph_objects as go
from typing import Dict, Any, List

class NetworkVisualizer:
    """
    Visualizes network graphs using Plotly.
    """
    
    def create_coupling_chart(self, coupling_data: Dict[str, Any]) -> go.Figure:
        """
        Create a network diagram of file coupling.
        coupling_data: Output from CouplingAnalyzer.
        """
        edges_data = coupling_data.get("coupling_edges", [])
        if not edges_data:
            return go.Figure()
            
        G = nx.Graph()
        for edge in edges_data:
            # We can filter weak edges here if needed
            G.add_edge(edge["source"], edge["target"], weight=edge["weight"])
            
        # Layout
        pos = nx.spring_layout(G, seed=42)
        
        # Edges
        edge_x = []
        edge_y = []
        texts = []
        
        for edge in G.edges(data=True):
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.append(x0)
            edge_x.append(x1)
            edge_x.append(None)
            edge_y.append(y0)
            edge_y.append(y1)
            edge_y.append(None)
            texts.append(f"Coupling: {edge[2].get('weight', 1)}")

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='text',
            text=texts,
            mode='lines')

        # Nodes
        node_x = []
        node_y = []
        node_text = []
        
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(str(node))

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers',
            hoverinfo='text',
            text=node_text,
            marker=dict(
                showscale=True,
                colorscale='YlGnBu',
                reversescale=True,
                color=[],
                size=10,
                colorbar=dict(
                    thickness=15,
                    title='Node Connections',
                    xanchor='left',
                    titleside='right'
                ),
                line_width=2))
                
        # Color by degree
        node_adjacencies = []
        for node, adjacencies in enumerate(G.adjacency()):
            node_adjacencies.append(len(adjacencies[1]))
            
        node_trace.marker.color = node_adjacencies

        fig = go.Figure(data=[edge_trace, node_trace],
             layout=go.Layout(
                title='Temporal Coupling Network',
                titlefont_size=16,
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                annotations=[ dict(
                    text="",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.005, y=-0.002 ) ],
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                )
                
        return fig
