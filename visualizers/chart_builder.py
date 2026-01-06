import plotly.graph_objs as go
import plotly.express as px
from typing import List, Dict, Any
from datetime import datetime

class ChartBuilder:
    """
    Builds visualizations for repository analysis.
    """
    
    def create_pattern_timeline(self, result: Dict[str, Any]) -> go.Figure:
        """
        Create a timeline of commits, highlighting bursts and regenerations.
        """
        # We need raw commits to plot them. 
        # Currently 'result' might not have all commits if they aren't passed down.
        # But 'result' is just a dict merged from analyzers.
        # We might need to pass the Repository object or stash commits in the result.
        # For now, let's look at what PatternAnalyzer returns. It returns 'bursts' and 'regenerations'.
        # We don't have a full list of commits in 'result' by default.
        # We should update CLI/PatternAnalyzer to ensure we have data to plot.
        # Or we can just plot the bursts and regenerations.
        
        bursts = result.get("bursts", [])
        regenerations = result.get("regenerations", [])
        
        fig = go.Figure()
        
        # Plot Bursts as rectangles
        for burst in bursts:
            start = burst.start_commit.date
            end = start + burst.duration
            # Ensure visible width
            if burst.duration.total_seconds() < 60:
                from datetime import timedelta
                end = start + timedelta(minutes=5)
                
            fig.add_vrect(
                x0=start, x1=end,
                fillcolor="rgba(255, 165, 0, 0.2)",
                layer="below",
                line_width=0,
                annotation_text="Burst",
                annotation_position="top left"
            )
            
        # Plot Regenerations (as points)
        regen_x = []
        regen_y = []
        regen_text = []
        
        for regen in regenerations:
            for commit in regen.commits:
                if commit.date:
                    regen_x.append(commit.date)
                    regen_y.append(commit.total_changes)
                    regen_text.append(f"Regeneration: {regen.filepath}<br>{commit.message}")
                    
        if regen_x:
            fig.add_trace(go.Scatter(
                x=regen_x, y=regen_y,
                mode='markers',
                marker=dict(color='red', size=10, symbol='diamond'),
                name='Regenerations',
                text=regen_text,
                hoverinfo='text'
            ))
            
        fig.update_layout(
            title="Collaboration Timeline (Patterns)",
            xaxis_title="Time",
            yaxis_title="Changes (Lines)",
            hovermode='closest'
        )
        
        return fig

    def create_hotspot_chart(self, hotspots: List[Any]) -> go.Figure:
        """
        Create a bar chart of top hotspots.
        hotspots: List of FileHotspot objects or dicts
        """
        if not hotspots:
            return go.Figure()

        # Extract data
        filepaths = [h.filepath for h in hotspots]
        counts = [h.change_count for h in hotspots]
        churns = [h.churn_rate for h in hotspots]
        
        fig = go.Figure(data=[
            go.Bar(name='Change Count', x=filepaths, y=counts),
            go.Scatter(name='Churn Rate', x=filepaths, y=churns, yaxis='y2', mode='lines+markers')
        ])
        
        fig.update_layout(
            title="Repository Hotspots",
            yaxis=dict(title="Change Count"),
            yaxis2=dict(title="Churn Rate", overlaying='y', side='right'),
            barmode='group',
            xaxis_tickangle=-45
        )
        
        return fig
        
    def create_summary_chart(self, metrics: Dict[str, Any]) -> go.Figure:
        """
        Create summary chart.
        For now, let's just make a simple gauge or indicator if we had more metrics.
        Since we don't have much summary data yet, returning empty or simple figure.
        """
        return go.Figure()
