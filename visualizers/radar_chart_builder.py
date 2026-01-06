import plotly.graph_objects as go
from typing import Dict, List

class RadarChartBuilder:
    """
    Builds radar charts to visualize multi-dimensional analysis scores.
    """
    
    def create_perspective_radar(self, aggregate_scores: Dict[str, float]) -> str:
        """
        Create a radar chart of perspective scores.
        Returns HTML div string.
        """
        if not aggregate_scores:
            return "<div>No perspective data available</div>"
            
        categories = list(aggregate_scores.keys())
        values = list(aggregate_scores.values())
        
        # Close the loop
        categories.append(categories[0])
        values.append(values[0])
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Code Quality'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=False,
            title="Code Quality Perspectives",
            height=400,
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
