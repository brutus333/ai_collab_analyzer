from typing import List, Dict, Any
from ai_collab_analyzer.models.recommendations import ActionableInsight, RecommendationSeverity

class RecommendationEngine:
    """
    Analyzes multiple metric dimensions to generate proactive collaboration insights.
    """
    
    def generate_recommendations(self, result: Dict[str, Any]) -> List[ActionableInsight]:
        insights = []
        
        health = result.get('health_score', 100)
        coherence = result.get('coherence_score', 100)
        risk = result.get('overall_risk_score', 0)
        prompts = result.get('prompts', [])
        hotspots = result.get('hotspots', [])
        
        def get_risk(path):
            rs = result.get('risk_scores', {})
            if isinstance(rs, dict):
                return rs.get(path, 0)
            if isinstance(rs, list):
                for item in rs:
                    if isinstance(item, dict):
                        f = item.get('file') or item.get('filepath')
                        s = item.get('risk_score') or item.get('score') or item.get('risk')
                        if f == path: return s or 0
            return 0

        # 1. High Risk + High Churn
        for hotspot in hotspots:
            if not isinstance(hotspot, dict): continue
            filepath = hotspot.get('filepath')
            churn = hotspot.get('churn_rate', 0)
            file_risk = get_risk(filepath)
            
            if file_risk > 50 and churn > 30:
                insights.append(ActionableInsight(
                    title=f"Critical Instability: {filepath}",
                    description=f"{filepath} has extremely high churn and risk score. This indicates it is a major bottleneck or source of technical debt.",
                    severity=RecommendationSeverity.CRITICAL,
                    affected_areas=[filepath],
                    action_item="Refactor into smaller modules or freeze changes for stability review.",
                    rationale="High churn combined with high risk scoring suggests architectural instability.",
                    category="Risk"
                ))

        # 2. Low Coherence + High Complexity
        if coherence < 60:
            insights.append(ActionableInsight(
                title="Low Code Coherence",
                description="The repository shows significant structural duplication or inconsistent implementation styles.",
                severity=RecommendationSeverity.HIGH,
                affected_areas=["Global Architecture"],
                action_item="Standardize code patterns and review duplication clusters.",
                rationale="A coherence score below 60 typically indicates that AI is generating code without a consistent structural template.",
                category="Architecture"
            ))

        # 3. Prompt Quality Check
        if len(prompts) > 0:
            avg_efficiency = result.get('prompt_efficiency', 0) # if we had it
            # Simple heuristic on prompt diversity/lack thereof
            if len(prompts) > 20 and len(set([p.get('content', '')[:20] for p in prompts])) < 5:
                insights.append(ActionableInsight(
                    title="Fragmented Prompting Pattern",
                    description="Detected repetitive prompts with slight variations, leading to high iteration cycles.",
                    severity=RecommendationSeverity.MEDIUM,
                    affected_areas=["Collaboration Workflow"],
                    action_item="Create standard prompt templates for recurring tasks.",
                    rationale="Repetitive minor variations in prompts often indicate the user is struggling to get the AI to follow instructions.",
                    category="Collaboration"
                ))

        # 4. Healthy Project Positive Reinforcement
        if health > 90 and risk < 10:
             insights.append(ActionableInsight(
                title="Maintain Momentum",
                description="Project health is excellent and risk is minimal.",
                severity=RecommendationSeverity.INFO,
                affected_areas=["All"],
                action_item="Continue current collaboration practices.",
                rationale="Metrics are within optimal industry ranges.",
                category="Status"
            ))

        return insights
