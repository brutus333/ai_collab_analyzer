from typing import List, Dict, Any
from .link_generator import LinkGenerator
from ..analyzers.health_analyzer import HealthAnalyzer
from ..visualizers.chart_builder import ChartBuilder
from ..visualizers.network_visualizer import NetworkVisualizer
from ..core.repository import Repository
from ..visualizers.radar_chart_builder import RadarChartBuilder
import json
import os

class HTMLReporter:
    """
    Generates HTML reports from analysis results.
    """
    
    def __init__(self):
        self.chart_builder = ChartBuilder()
        self.network_visualizer = NetworkVisualizer()
        self.radar_builder = RadarChartBuilder()
        
    def generate_report(self, repository: Repository, analysis_result: Dict[str, Any]):
        """
        Generate HTML content for the report.
        """
        health_score = analysis_result.get("health_score", 0)
        hotspots = analysis_result.get("hotspots", [])
        
        # Initialize LinkGenerator
        link_gen = LinkGenerator(repository.remote_url)
        summary = analysis_result.get("summary", "")
        
        # Create charts
        hotspot_chart = self.chart_builder.create_hotspot_chart(hotspots)
        hotspot_div = hotspot_chart.to_html(full_html=False, include_plotlyjs=False) if hotspot_chart else "<div>No data</div>"
        
        coupling_chart = self.network_visualizer.create_coupling_chart(analysis_result)
        coupling_div = coupling_chart.to_html(full_html=False, include_plotlyjs=False) if coupling_chart else "<div>No coupling data</div>"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>AI Collaboration Analysis Report</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body {{ font-family: sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                .score {{ font-size: 2em; font-weight: bold; color: {'green' if health_score > 80 else 'orange' if health_score > 50 else 'red'}; }}
                .section {{ margin-bottom: 30px; border: 1px solid #ddd; padding: 20px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <h1>Repository Health Report</h1>
            
            <div class="section">
                <h2>Summary</h2>
                <p>{summary}</p>
                <div class="score">Health Score: {health_score:.2f}</div>
            </div>

            <div class="section">
                <h2>Code Quality Perspectives</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <h3>Composite Quality</h3>
                        <div class="score" style="color: {'green' if analysis_result.get('composite_quality_score', 0) > 70 else 'orange' if analysis_result.get('composite_quality_score', 0) > 40 else 'red'}">
                            {analysis_result.get('composite_quality_score', 0):.1f}
                        </div>
                    </div>
                </div>
                
                <div style="display: flex; flex-wrap: wrap;">
                    <div style="flex: 1; min-width: 400px;">
                        {self.radar_builder.create_perspective_radar(analysis_result.get('perspective_scores', {}))}
                    </div>
                    <div style="flex: 1; min-width: 400px;">
                        <h3>Critical Quality Findings</h3>
                        <table>
                            <tr>
                                <th>Finding</th>
                                <th>Severity</th>
                                <th>Location</th>
                            </tr>
                            {
                                "".join([
                                    f'<tr><td>{f.title}</td><td style="color: {"red" if f.severity.value == "critical" else "orange"}; font-weight: bold;">{f.severity.value.upper()}</td><td>{f.location.filepath if f.location else "Global"}</td></tr>'
                                    for f in analysis_result.get('critical_findings', [])[:10]
                                ]) or "<tr><td colspan='3'>No critical quality issues found.</td></tr>"
                            }
                        </table>
                    </div>
                </div>

                {
                    "".join([
                        f"""
                        <div style="margin-top: 20px; padding: 15px; background: #f9f9f9; border-left: 5px solid #007bff;">
                            <h3>{p.perspective_name} Details ({p.score:.1f}%)</h3>
                            <div style="display: flex; gap: 20px;">
                                <div style="flex: 1;">
                                    <h4>Dimension Scores</h4>
                                    <ul>
                                        {"".join([f"<li><strong>{d.name}:</strong> {d.score:.1f}%</li>" for d in p.dimensions])}
                                    </ul>
                                </div>
                                <div style="flex: 2;">
                                    <h4>Key Recommendations</h4>
                                    <ul>
                                        {"".join([f"<li>{rec}</li>" for rec in p.recommendations[:5]]) or "<li>Maintain current practices.</li>"}
                                    </ul>
                                </div>
                            </div>
                        </div>
                        """
                        for p in analysis_result.get('perspective_details', [])
                        if p.score < 100
                    ])
                }
            </div>
            
            <div class="section">
                <h2>Collaboration Patterns</h2>
                <p><strong>Burst Patterns Detected:</strong> {analysis_result.get('burst_patterns_count', 0)}</p>
                <p><strong>Regenerations Suspected:</strong> {analysis_result.get('regeneration_cycles_count', 0)}</p>
                
                <h3>Timeline</h3>
                {self.chart_builder.create_pattern_timeline(analysis_result).to_html(full_html=False, include_plotlyjs=False)}
            </div>
            
            <div class="section">
                <h2>Prompt Engineering Evolution</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <h3>Total Prompts Detected</h3>
                        <p>{analysis_result.get('total_prompts', 0)}</p>
                    </div>
                    <div class="stat-card">
                        <h3>Prompts per Commit</h3>
                        <p>{analysis_result.get('prompt_frequency_per_commit', 0):.2f}</p>
                    </div>
                    <div class="stat-card">
                        <h3>Avg Sentiment</h3>
                        <p>{analysis_result.get('sentiment_avg', 0):.2f}</p>
                    </div>
                    <div class="stat-card">
                        <h3>Prompt Efficiency</h3>
                        <p>{analysis_result.get('efficiency_score', 0):.1f}%</p>
                    </div>
                    <div class="stat-card">
                        <h3>AI Skill Level</h3>
                        <p>{analysis_result.get('learning_curve').skill_level if analysis_result.get('learning_curve') else 'Unknown'}</p>
                    </div>
                    <div class="stat-card">
                        <h3>Growth Trend</h3>
                        <p>{"+" if (analysis_result.get('learning_curve').improvement_rate if analysis_result.get('learning_curve') else 0) > 0 else ""}{analysis_result.get('learning_curve').improvement_rate if analysis_result.get('learning_curve') else 0:.1f}%</p>
                    </div>
                </div>
                
                <p><strong>Top Themes:</strong> {", ".join(analysis_result.get('top_topics', [])) or "None detected"}</p>
                
                <h3>Detected Prompts</h3>
                <table>
                    <tr>
                        <th>Source</th>
                        <th>Location</th>
                        <th>Content</th>
                    </tr>
                    {
                        "".join([
                            f"<tr><td>{p.source_type}</td><td>{self._linkify_location(p, link_gen)}</td><td>{p.content}</td></tr>"
                            for p in analysis_result.get('prompts', [])
                        ]) or "<tr><td colspan='3'>No prompts detected</td></tr>"
                    }
                </table>
            </div>

            <div class="section">
                <h2>AI Instruction Impact</h2>
                <p>Measures how changes to requirements or instructions in documentation correlate with code stability.</p>
                <table>
                    <tr>
                        <th>Instruction Change</th>
                        <th>Commit</th>
                        <th>Metric Impact</th>
                    </tr>
                    {
                        "".join([
                            f'<tr><td><code>{c.instruction[:80]}...</code></td><td>{c.commit_hash}</td><td style="color: {"#28a745" if c.impact_score > 0 else "#dc3545"}; font-weight: bold;">{c.context}</td></tr>'
                            for c in analysis_result.get('instructional_correlations', [])
                        ]) or "<tr><td colspan='3'>No significant instructional correlations detected yet.</td></tr>"
                    }
                </table>
            </div>
            
            <div class="section">
                <h2>Temporal Coupling Graph</h2>
                {coupling_div}
                <p>Displays files that frequently change together in the same commit.</p>
            </div>

            <div class="section">
                <h2>Code Coherence</h2>
                <div class="score">Coherence Score: {analysis_result.get('coherence_score', 0):.2f}</div>
                <p>Measures architectural consistency and code reuse. Higher is better.</p>
                
                <h3>Duplication Clusters</h3>
                <table>
                    <tr>
                        <th>Cluster ID</th>
                        <th>Files Affected</th>
                        <th>Similarity</th>
                        <th>Snippet</th>
                    </tr>
                    {
                        "".join([
                            f"<tr><td>{c.cluster_id}</td><td>{', '.join(c.files)}</td><td>{c.similarity_score:.1f}%</td><td><code>{c.code_snippet}</code></td></tr>"
                            for c in analysis_result.get('duplication_clusters', [])
                        ]) or "<tr><td colspan='4'>No significant duplication detected.</td></tr>"
                    }
                </table>
            </div>
            
            <div class="section">
                <h2>Future Risks & Predictions</h2>
                <div class="score" style="color: {'red' if (analysis_result.get('overall_risk_score', 0)) > 60 else 'orange' if (analysis_result.get('overall_risk_score', 0)) > 30 else 'green'}">
                    Risk Score: {analysis_result.get('overall_risk_score', 0):.2f}
                </div>
                
                {
                    "".join([
                        f'<div style="background: #fff3f3; border-left: 5px solid red; padding: 10px; margin: 10px 0;"><strong>{w.severity}: {w.title}</strong><br>{w.message}</div>'
                        for w in analysis_result.get('warnings', [])
                    ])
                }

                <h3>File Risk Map</h3>
                <table>
                    <tr>
                        <th>File</th>
                        <th>Risk Score</th>
                        <th>Trend</th>
                        <th>Factors</th>
                    </tr>
                    {
                        "".join([
                            f"<tr><td>{r.filepath}</td><td>{r.score:.1f}%</td><td>{r.trend}</td><td>{', '.join([f.name for f in r.factors])}</td></tr>"
                            for r in analysis_result.get('risk_scores', [])[:10]
                        ])
                    }
                </table>

                <h3>Activity Forecast</h3>
                <p>Projected cumulative churn (additions + deletions) based on current velocity.</p>
                <div id="forecast_chart"></div>
                <script>
                    var hist_x = {json.dumps([p.timestamp.strftime('%Y-%m-%d') for p in (analysis_result.get('forecasts')[0].historical_data if analysis_result.get('forecasts') else [])])};
                    var hist_y = {json.dumps([p.value for p in (analysis_result.get('forecasts')[0].historical_data if analysis_result.get('forecasts') else [])])};
                    var fore_x = {json.dumps([p.timestamp.strftime('%Y-%m-%d') for p in (analysis_result.get('forecasts')[0].forecasted_data if analysis_result.get('forecasts') else [])])};
                    var fore_y = {json.dumps([p.value for p in (analysis_result.get('forecasts')[0].forecasted_data if analysis_result.get('forecasts') else [])])};
                    
                    var trace1 = {{ x: hist_x, y: hist_y, mode: 'lines', name: 'Historical' }};
                    var trace2 = {{ x: fore_x, y: fore_y, mode: 'lines', name: 'Forecasted', line: {{ dash: 'dot', color: 'red' }} }};
                    Plotly.newPlot('forecast_chart', [trace1, trace2], {{ title: 'Cumulative Churn Forecast' }});
                </script>
            </div>

            <div class="section">
                <h2>Hotspots</h2>
                {hotspot_div}
            </div>
            
            <div class="section">
                <h2>Raw Data</h2>
                <pre>{json.dumps(self._serialize_hotspots(hotspots), indent=2)}</pre>
            </div>
        </body>
        </html>
        """
        return html
        
    def save_report(self, html: str, output_path: str):
        """
        Save the report to a file.
        """
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
            
    def _linkify_location(self, prompt, link_gen):
        location = prompt.filepath if prompt.filepath else ""
        if prompt.line_number:
            location += f" : {prompt.line_number}"
            
        if prompt.source_type == "commit_message" and prompt.filepath: # We stored hash in filepath for commits
            link = link_gen.generate_commit_link(prompt.filepath)
            if link:
                return f'<a href="{link}" target="_blank">{prompt.filepath}</a>'
        elif prompt.filepath:
            link = link_gen.generate_file_link(prompt.filepath)
            if link:
                return f'<a href="{link}" target="_blank">{location}</a>'
                
        return location

    def _serialize_hotspots(self, hotspots: List[Any]) -> List[Dict]:
        """Convert objects to dicts for JSON"""
        return [
            {
                "filepath": h.filepath,
                "change_count": h.change_count,
                "churn_rate": h.churn_rate
            }
            for h in hotspots
        ]
