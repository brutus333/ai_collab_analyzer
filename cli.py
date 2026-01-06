import argparse
import sys
import os
from typing import List
from ai_collab_analyzer.extractors.git_extractor import GitExtractor
from ai_collab_analyzer.analyzers.health_analyzer import HealthAnalyzer
from ai_collab_analyzer.analyzers.pattern_analyzer import PatternAnalyzer
from ai_collab_analyzer.analyzers.coupling_analyzer import CouplingAnalyzer
from ai_collab_analyzer.analyzers.prompt_analyzer import PromptAnalyzer
from ai_collab_analyzer.analyzers.coherence_analyzer import CoherenceAnalyzer
from ai_collab_analyzer.analyzers.predictive_analyzer import PredictiveAnalyzer
from ai_collab_analyzer.analyzers.multi_perspective_analyzer import MultiPerspectiveAnalyzer
from ai_collab_analyzer.reporters.html_reporter import HTMLReporter
from ai_collab_analyzer.visualizers.radar_chart_builder import RadarChartBuilder
from ai_collab_analyzer.storage.database import DatabaseManager
from ai_collab_analyzer.multi_repo.comparator import RepositoryComparator
import subprocess
import time
from datetime import datetime, date

class CLI:
    def parse_arguments(self):
        parser = argparse.ArgumentParser(description="AI Collaboration Pattern Analyzer")
        subparsers = parser.add_subparsers(dest='command', help='Commands')
        
        # Analyze command
        analyze_parser = subparsers.add_parser('analyze', help='Analyze a repository')
        analyze_parser.add_argument('path', help='Path to git repository')
        analyze_parser.add_argument('--output', '-o', default='report.html', help='Output path for report')
        
        # Serve command
        serve_parser = subparsers.add_parser('serve', help='Launch interactive dashboard')
        
        # Compare command
        compare_parser = subparsers.add_parser('compare', help='Compare multiple repositories')
        compare_parser.add_argument('repos', nargs='+', help='Names of repositories to compare')
        
        return parser.parse_args()
        
    def run_analysis(self, repo_path: str, output_path: str):
        print(f"Analyzing repository at: {repo_path}")
        
        try:
            # 1. Extract
            print("Step 1/3: Extracting repository data...")
            extractor = GitExtractor()
            repository = extractor.extract_repository(repo_path)
            print(f"  Found {len(repository.commits)} commits and {len(repository.files)} files.")
            
            # 2. Analyze
            print("Step 2/3: Analyzing patterns...")
            analyzer = HealthAnalyzer()
            health_result = analyzer.analyze(repository)
            
            # Run Pattern Analysis
            pattern_analyzer = PatternAnalyzer()
            pattern_results = pattern_analyzer.analyze(repository)
            
            # Run Coupling Analysis
            coupling_analyzer = CouplingAnalyzer()
            coupling_results = coupling_analyzer.analyze(repository)
            
            # Run Prompt Analysis
            prompt_analyzer = PromptAnalyzer()
            prompt_results = prompt_analyzer.analyze(repository)
            
            # Run Coherence Analysis
            coherence_analyzer = CoherenceAnalyzer()
            coherence_results = coherence_analyzer.analyze(repository)
            
            # Run Predictive Analysis
            predictive_analyzer = PredictiveAnalyzer()
            predictive_results = predictive_analyzer.analyze(repository)
            
            # Run Multi-Perspective Analysis
            perspective_analyzer = MultiPerspectiveAnalyzer()
            perspective_results = perspective_analyzer.analyze(repository)
            
            # Combine results
            result = {
                **health_result,
                **pattern_results,
                **coupling_results,
                # Prompt insights
                "total_prompts": prompt_results.total_prompts,
                "prompts": prompt_results.prompts,
                "prompt_frequency_per_commit": prompt_results.prompt_frequency_per_commit,
                "sentiment_avg": prompt_results.sentiment_avg,
                "efficiency": prompt_results.efficiency,
                "learning_curve": prompt_results.learning_curve,
                "top_topics": prompt_results.top_topics,
                "sentiment_summary": prompt_results.sentiment_summary,
                "frustration_trend": prompt_results.frustration_trend,
                "instructional_correlations": prompt_results.instructional_correlations,
                "efficiency_score": prompt_results.efficiency.overall_score,
                # Coherence
                "coherence_score": coherence_results.coherence_score,
                "duplication_clusters": coherence_results.duplication_clusters,
                # Predictive
                "overall_risk_score": predictive_results.overall_risk_score,
                "risk_scores": predictive_results.risk_scores,
                "forecasts": predictive_results.forecasts,
                "warnings": predictive_results.warnings,
                # Multi-Perspective
                "perspective_scores": perspective_results.aggregate_scores,
                "perspective_details": perspective_results.perspective_results,
                "critical_findings": perspective_results.critical_findings,
                "composite_quality_score": perspective_results.composite_score
            }
            
            print(f"  Health Score: {result.get('health_score', 'N/A'):.2f}")
            print(f"  Bursts Detected: {result.get('burst_patterns_count', 'N/A')}")
            print(f"  Coupled Pairs: {len(result.get('coupling_edges', []))}")
            print(f"  Total Prompts Found: {result.get('total_prompts', 'N/A')}")
            print(f"  Coherence Score: {result.get('coherence_score', 'N/A'):.2f}")
            print(f"  Duplication Clusters: {len(result.get('duplication_clusters', []))}")
            print(f"  Overall Risk Score: {result.get('overall_risk_score', 'N/A'):.2f}")
            print(f"  Quality Score: {result.get('composite_quality_score', 'N/A'):.2f}")
            print(f"  Active Warnings: {len(result.get('warnings', []))}")
            
            # 3. Save to Database
            print("Step 3/4: Saving results to database...")
            db = DatabaseManager()
            repo_name = os.path.basename(os.path.abspath(repo_path))
            from dataclasses import asdict, is_dataclass
            
            def make_serializable(obj):
                if isinstance(obj, (list, tuple)):
                    return [make_serializable(v) for v in obj]
                if isinstance(obj, dict):
                    return {k: make_serializable(v) for k, v in obj.items()}
                if is_dataclass(obj):
                    return make_serializable(asdict(obj))
                if isinstance(obj, (datetime, date)):
                    return obj.isoformat()
                try:
                    # Try to see if it's already JSON serializable
                    import json
                    json.dumps(obj)
                    return obj
                except (TypeError, OverflowError):
                    return str(obj)

            serializable_result = make_serializable(result)
            db.save_analysis(repo_name, repo_path, serializable_result)

            # 4. Report
            print("Step 4/4: Generating report...")
            reporter = HTMLReporter()
            html = reporter.generate_report(repository, result)
            reporter.save_report(html, output_path)
            print(f"  Report saved to: {output_path}")
            
            print("\nAnalysis Success!")
            
        except Exception as e:
            print(f"\nError during analysis: {str(e)}")
            sys.exit(1)

    def handle_serve(self):
        print("🚀 Launching AI Collaboration Dashboard...")
        # Start API in background
        api_proc = subprocess.Popen([sys.executable, "-m", "uvicorn", "ai_collab_analyzer.web.api.app:app"])
        # Give API a second to start
        time.sleep(2)
        # Start Streamlit
        st_proc = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "ai_collab_analyzer/web/dashboard/app.py"])
        
        try:
            print("Dashboard is running. Press Ctrl+C to stop.")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down servers...")
            api_proc.terminate()
            st_proc.terminate()

    def handle_compare(self, repo_names: List[str]):
        print(f"📊 Comparing repositories: {', '.join(repo_names)}...")
        db = DatabaseManager()
        comparator = RepositoryComparator(db)
        results = comparator.compare(repo_names)
        
        if not results['comparison']:
            print("  No matching repositories found in database.")
            return

        print("\nComparison Results:")
        for r in results['comparison']:
            print(f"  - {r['name']}: Health={r['health']:.1f}, Coherence={r['coherence']:.1f}, Risk={r['risk']:.2f}")
        
        print("\nInsights:")
        for insight in results['insights']:
            print(f"  💡 {insight}")

def main():
    cli = CLI()
    args = cli.parse_arguments()
    
    if args.command == 'analyze':
        cli.run_analysis(args.path, args.output)
    elif args.command == 'serve':
        cli.handle_serve()
    elif args.command == 'compare':
        cli.handle_compare(args.repos)
    else:
        # Default help if no command
        print("Please specify a command (analyze, serve, or compare). Use --help for usage.")
        sys.exit(1)

if __name__ == "__main__":
    main()
