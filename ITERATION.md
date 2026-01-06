# Software Architecture: Human-AI Collaboration Pattern Analyzer

## Architecture Principles

- **Layered Architecture**: Data → Analysis → Insights → Presentation
- **Progressive Enhancement**: Each iteration adds layers without breaking previous ones
- **Plugin-Based Analyzers**: Each analyzer is independent and composable
- **Separation of Concerns**: Data extraction, analysis, and presentation are decoupled
- **Single Responsibility**: Each class has one clear purpose
- **Open-Closed**: Open for extension, closed for modification

---

## Iteration 1: Repository Health Scanner

### Package Structure
```
ai_collab_analyzer/
├── core/
│   ├── repository.py
│   ├── commit.py
│   └── file_history.py
├── extractors/
│   └── git_extractor.py
├── analyzers/
│   ├── base_analyzer.py
│   └── health_analyzer.py
├── metrics/
│   └── basic_metrics.py
├── visualizers/
│   └── chart_builder.py
├── reporters/
│   └── html_reporter.py
└── cli.py
```

### Core Module

#### `repository.py`
```
Class: Repository
Responsibilities:
- Represent a Git repository
- Store repository metadata (path, name, url)
- Provide access to commit history
- Cache repository data

Methods:
- __init__(path: str)
- get_commits() -> List[Commit]
- get_files() -> List[str]
- get_file_history(filepath: str) -> FileHistory
- get_metadata() -> Dict
```

#### `commit.py`
```
Class: Commit
Responsibilities:
- Represent a single Git commit
- Store commit metadata (hash, author, date, message)
- Provide access to changed files
- Calculate commit metrics

Properties:
- hash: str
- author: str
- date: datetime
- message: str
- changed_files: List[str]
- additions: int
- deletions: int
- total_changes: int

Methods:
- __init__(commit_data: dict)
- is_merge() -> bool
- get_size() -> int
```

#### `file_history.py`
```
Class: FileHistory
Responsibilities:
- Track history of a single file
- Store all commits affecting the file
- Calculate file-specific metrics

Properties:
- filepath: str
- commits: List[Commit]
- total_changes: int
- creation_date: datetime
- last_modified: datetime

Methods:
- __init__(filepath: str)
- add_commit(commit: Commit)
- get_churn_rate() -> float
- get_change_frequency() -> float
```

### Extractors Module

#### `git_extractor.py`
```
Class: GitExtractor
Responsibilities:
- Extract data from Git repository using PyDriller
- Convert Git data to internal models
- Handle repository cloning if needed

Methods:
- __init__()
- extract_repository(path: str) -> Repository
- extract_commits(repo_path: str) -> List[Commit]
- extract_file_histories(repo_path: str) -> Dict[str, FileHistory]
```

### Analyzers Module

#### `base_analyzer.py`
```
Class: BaseAnalyzer (Abstract)
Responsibilities:
- Define analyzer interface
- Provide common analyzer functionality
- Handle caching of analysis results

Methods (Abstract):
- analyze(repository: Repository) -> AnalysisResult
- get_name() -> str
- get_description() -> str

Methods (Concrete):
- cache_result(key: str, value: Any)
- get_cached_result(key: str) -> Optional[Any]
```

#### `health_analyzer.py`
```
Class: HealthAnalyzer(BaseAnalyzer)
Responsibilities:
- Analyze overall repository health
- Calculate health score
- Identify basic patterns

Methods:
- analyze(repository: Repository) -> HealthAnalysisResult
- calculate_health_score(repository: Repository) -> float
- identify_hotspots(repository: Repository) -> List[FileHotspot]
- analyze_commit_velocity(repository: Repository) -> VelocityMetrics

Class: HealthAnalysisResult
Properties:
- health_score: float
- hotspots: List[FileHotspot]
- velocity_metrics: VelocityMetrics
- summary: str
```

### Metrics Module

#### `basic_metrics.py`
```
Class: MetricsCalculator
Responsibilities:
- Calculate basic repository metrics
- Provide statistical functions
- Aggregate data for reporting

Methods:
- calculate_churn_rate(file_history: FileHistory) -> float
- calculate_commit_frequency(commits: List[Commit], period: str) -> Dict
- calculate_file_hotspots(repository: Repository, top_n: int) -> List[tuple]
- calculate_commit_size_distribution(commits: List[Commit]) -> Dict

Class: FileHotspot
Properties:
- filepath: str
- change_count: int
- churn_rate: float
- risk_score: float
```

### Visualizers Module

#### `chart_builder.py`
```
Class: ChartBuilder
Responsibilities:
- Create visualizations using Plotly
- Generate charts for reports
- Provide consistent styling

Methods:
- create_timeline_chart(data: pd.DataFrame) -> plotly.graph_objs.Figure
- create_hotspot_chart(hotspots: List[FileHotspot]) -> plotly.graph_objs.Figure
- create_distribution_chart(data: Dict) -> plotly.graph_objs.Figure
- apply_theme(figure: plotly.graph_objs.Figure) -> plotly.graph_objs.Figure
```

### Reporters Module

#### `html_reporter.py`
```
Class: HTMLReporter
Responsibilities:
- Generate HTML reports
- Combine metrics and visualizations
- Export to file and JSON

Methods:
- __init__(template_path: str)
- generate_report(analysis_results: List[AnalysisResult]) -> str
- save_report(html: str, output_path: str)
- export_json(analysis_results: List[AnalysisResult]) -> str
```

### CLI Module

#### `cli.py`
```
Class: CLI
Responsibilities:
- Command-line interface
- Parse arguments
- Orchestrate analysis workflow

Methods:
- main()
- parse_arguments() -> argparse.Namespace
- run_analysis(repo_path: str, output_path: str)
```

---

## Iteration 2: Change Pattern Detector

### New/Modified Packages
```
ai_collab_analyzer/
├── analyzers/
│   ├── pattern_analyzer.py      # NEW
│   └── fix_detector.py          # NEW
├── metrics/
│   └── pattern_metrics.py       # NEW
└── models/
    └── change_patterns.py       # NEW
```

### New Analyzers

#### `pattern_analyzer.py`
```
Class: PatternAnalyzer(BaseAnalyzer)
Responsibilities:
- Detect change patterns in commit history
- Identify burst patterns
- Detect regeneration cycles
- Track stability timelines

Methods:
- analyze(repository: Repository) -> PatternAnalysisResult
- detect_burst_patterns(commits: List[Commit]) -> List[BurstPattern]
- detect_regenerations(file_history: FileHistory) -> List[Regeneration]
- calculate_stability_timeline(repository: Repository) -> Dict[str, datetime]

Class: PatternAnalysisResult
Properties:
- burst_patterns: List[BurstPattern]
- regenerations: Dict[str, List[Regeneration]]
- stability_timeline: Dict[str, datetime]
- fix_ratio: float
```

#### `fix_detector.py`
```
Class: FixDetector
Responsibilities:
- Detect fix commits using NLP
- Classify commit types
- Identify fix cascades

Methods:
- is_fix_commit(commit: Commit) -> bool
- classify_commit(commit: Commit) -> CommitType
- detect_fix_cascades(commits: List[Commit]) -> List[FixCascade]
- extract_keywords(message: str) -> List[str]

Enum: CommitType
Values:
- FEATURE
- FIX
- REFACTOR
- REGENERATION
- UNKNOWN
```

### New Models

#### `change_patterns.py`
```
Class: BurstPattern
Properties:
- start_commit: Commit
- following_fixes: List[Commit]
- affected_files: List[str]
- duration: timedelta
- severity: float

Class: Regeneration
Properties:
- file: str
- commits: List[Commit]
- reason: str (inferred)
- count: int

Class: FixCascade
Properties:
- initial_commit: Commit
- related_fixes: List[Commit]
- affected_files: Set[str]
- cascade_depth: int
```

### Modified/Enhanced

#### `basic_metrics.py` (Enhanced)
```
# Add new methods:
- calculate_fix_ratio(commits: List[Commit]) -> float
- calculate_regeneration_count(file_history: FileHistory) -> int
- calculate_time_to_stability(file_history: FileHistory) -> Optional[timedelta]
```

---

## Iteration 3: Human Intervention Mapper

### New/Modified Packages
```
ai_collab_analyzer/
├── analyzers/
│   └── intervention_analyzer.py  # NEW
├── extractors/
│   └── blame_extractor.py        # NEW
├── classifiers/
│   └── commit_classifier.py      # NEW
└── models/
    └── interventions.py          # NEW
```

### New Analyzers

#### `intervention_analyzer.py`
```
Class: InterventionAnalyzer(BaseAnalyzer)
Responsibilities:
- Analyze human intervention patterns
- Calculate touch ratios
- Map intervention intensity
- Identify AI strength/struggle zones

Methods:
- analyze(repository: Repository) -> InterventionAnalysisResult
- calculate_touch_ratio(file_history: FileHistory) -> float
- classify_edit_sizes(commits: List[Commit]) -> Dict[CommitSize, List[Commit]]
- map_intervention_zones(repository: Repository) -> InterventionMap
- identify_author_patterns(repository: Repository) -> Dict[str, AuthorPattern]

Class: InterventionAnalysisResult
Properties:
- touch_ratios: Dict[str, float]
- intervention_map: InterventionMap
- ai_strength_zones: List[str]
- ai_struggle_zones: List[str]
- author_patterns: Dict[str, AuthorPattern]
```

### New Extractors

#### `blame_extractor.py`
```
Class: BlameExtractor
Responsibilities:
- Extract Git blame data
- Track line-level authorship
- Calculate contribution percentages

Methods:
- extract_blame(repo_path: str, filepath: str) -> FileBlame
- calculate_author_contributions(file_blame: FileBlame) -> Dict[str, float]
- get_line_history(repo_path: str, filepath: str, line_num: int) -> List[Commit]

Class: FileBlame
Properties:
- filepath: str
- lines: List[BlameLine]
- author_stats: Dict[str, int]

Class: BlameLine
Properties:
- line_number: int
- content: str
- author: str
- commit: Commit
- age: timedelta
```

### New Classifiers

#### `commit_classifier.py`
```
Class: CommitClassifier
Responsibilities:
- Classify commits by size and type
- Use heuristics to identify AI vs human commits
- Detect edit patterns

Methods:
- classify_size(commit: Commit) -> CommitSize
- classify_origin(commit: Commit) -> CommitOrigin
- detect_edit_pattern(commits: List[Commit]) -> EditPattern
- calculate_signature(commit: Commit) -> CommitSignature

Enum: CommitSize
Values:
- TINY (< 10 lines)
- SMALL (10-50 lines)
- MEDIUM (50-200 lines)
- LARGE (200-1000 lines)
- HUGE (> 1000 lines)

Enum: CommitOrigin
Values:
- LIKELY_AI
- LIKELY_HUMAN
- UNCERTAIN

Class: CommitSignature
Properties:
- size: CommitSize
- file_count: int
- completeness: float
- style_consistency: float
```

### New Models

#### `interventions.py`
```
Class: InterventionMap
Properties:
- file_interventions: Dict[str, InterventionMetrics]
- module_interventions: Dict[str, InterventionMetrics]
- timeline: List[InterventionEvent]

Class: InterventionMetrics
Properties:
- filepath: str
- total_edits: int
- human_edits: int
- ai_edits: int
- touch_ratio: float
- intervention_frequency: float

Class: InterventionEvent
Properties:
- timestamp: datetime
- file: str
- edit_type: str
- size: CommitSize
- author: str

Class: AuthorPattern
Properties:
- author: str
- commit_size_distribution: Dict[CommitSize, int]
- primary_edit_type: str
- activity_timeline: List[datetime]
- collaboration_style: str
```

---

## Iteration 4: Temporal Coupling Analyzer

### New/Modified Packages
```
ai_collab_analyzer/
├── analyzers/
│   └── coupling_analyzer.py      # NEW
├── graph/
│   ├── dependency_graph.py       # NEW
│   └── coupling_graph.py         # NEW
└── models/
    └── coupling.py               # NEW
```

### New Analyzers

#### `coupling_analyzer.py`
```
Class: CouplingAnalyzer(BaseAnalyzer)
Responsibilities:
- Detect temporal coupling between files
- Identify co-change patterns
- Reconstruct prompt sessions
- Detect fix cascades
- Calculate coupling strength

Methods:
- analyze(repository: Repository) -> CouplingAnalysisResult
- detect_cochanges(repository: Repository) -> List[CouplingPair]
- reconstruct_sessions(commits: List[Commit]) -> List[PromptSession]
- detect_fix_cascades(repository: Repository) -> List[FixCascade]
- calculate_coupling_strength(file1: str, file2: str, commits: List[Commit]) -> float
- identify_hidden_dependencies(coupling_pairs: List[CouplingPair]) -> List[HiddenDependency]

Class: CouplingAnalysisResult
Properties:
- coupling_pairs: List[CouplingPair]
- coupling_graph: CouplingGraph
- prompt_sessions: List[PromptSession]
- hidden_dependencies: List[HiddenDependency]
- cascade_risks: Dict[str, float]
```

### New Graph Module

#### `dependency_graph.py`
```
Class: DependencyGraph
Responsibilities:
- Build and manage dependency graphs
- Calculate graph metrics
- Identify clusters and communities

Methods:
- __init__()
- add_node(node_id: str, attributes: Dict)
- add_edge(source: str, target: str, weight: float)
- get_neighbors(node_id: str) -> List[str]
- calculate_centrality() -> Dict[str, float]
- find_clusters() -> List[Set[str]]
- export_to_networkx() -> nx.Graph
```

#### `coupling_graph.py`
```
Class: CouplingGraph(DependencyGraph)
Responsibilities:
- Specialized graph for temporal coupling
- Visualize coupling relationships
- Identify coupling hotspots

Methods:
- add_coupling(file1: str, file2: str, strength: float, changes: List[Commit])
- get_coupling_strength(file1: str, file2: str) -> float
- find_coupling_hotspots(threshold: float) -> List[str]
- identify_coupling_clusters() -> List[CouplingCluster]
- generate_visualization() -> plotly.graph_objs.Figure
```

### New Models

#### `coupling.py`
```
Class: CouplingPair
Properties:
- file1: str
- file2: str
- strength: float
- cochange_count: int
- commits: List[Commit]
- confidence: float

Class: PromptSession
Properties:
- session_id: str
- timestamp: datetime
- files_created: List[str]
- files_modified: List[str]
- commit: Commit
- inferred_prompt_type: str

Class: HiddenDependency
Properties:
- files: Set[str]
- coupling_strength: float
- evidence: List[Commit]
- risk_level: str
- suggested_refactoring: str

Class: CouplingCluster
Properties:
- files: Set[str]
- internal_coupling: float
- external_coupling: float
- cohesion_score: float
```

---

## Iteration 5: Code Coherence Analyzer

### New/Modified Packages
```
ai_collab_analyzer/
├── analyzers/
│   └── coherence_analyzer.py     # NEW
├── parsers/
│   ├── ast_parser.py             # NEW
│   └── language_detector.py      # NEW
├── similarity/
│   ├── code_similarity.py        # NEW
│   └── pattern_matcher.py        # NEW
└── models/
    └── coherence.py              # NEW
```

### New Analyzers

#### `coherence_analyzer.py`
```
Class: CoherenceAnalyzer(BaseAnalyzer)
Responsibilities:
- Analyze code consistency and coherence
- Detect architectural drift
- Find duplicate patterns
- Measure style consistency
- Assess naming conventions

Methods:
- analyze(repository: Repository) -> CoherenceAnalysisResult
- analyze_pattern_consistency(repository: Repository) -> PatternConsistencyReport
- detect_architectural_drift(repository: Repository) -> List[DriftEvent]
- find_duplicates(repository: Repository) -> List[DuplicationCluster]
- analyze_naming_consistency(repository: Repository) -> NamingReport
- calculate_coherence_score(repository: Repository) -> float

Class: CoherenceAnalysisResult
Properties:
- coherence_score: float
- pattern_consistency: PatternConsistencyReport
- architectural_drift: List[DriftEvent]
- duplications: List[DuplicationCluster]
- naming_report: NamingReport
- style_variance: float
```

### New Parsers Module

#### `ast_parser.py`
```
Class: ASTParser
Responsibilities:
- Parse source code into AST
- Extract structural patterns
- Support multiple languages via Tree-sitter

Methods:
- parse_file(filepath: str, language: str) -> AST
- extract_functions(ast: AST) -> List[FunctionNode]
- extract_classes(ast: AST) -> List[ClassNode]
- extract_patterns(ast: AST) -> List[CodePattern]
- get_complexity_metrics(ast: AST) -> ComplexityMetrics

Class: AST
Properties:
- root: Node
- language: str
- filepath: str

Methods:
- traverse(visitor: ASTVisitor)
- find_nodes(node_type: str) -> List[Node]
```

#### `language_detector.py`
```
Class: LanguageDetector
Responsibilities:
- Detect programming language from file
- Provide language-specific parsing

Methods:
- detect_language(filepath: str) -> str
- get_parser_for_language(language: str) -> ASTParser
- is_supported(language: str) -> bool
```

### New Similarity Module

#### `code_similarity.py`
```
Class: CodeSimilarityAnalyzer
Responsibilities:
- Compare code similarity
- Detect near-duplicates
- Find pattern repetition

Methods:
- calculate_similarity(code1: str, code2: str) -> float
- find_similar_functions(functions: List[FunctionNode]) -> List[SimilarityGroup]
- detect_duplicates(repository: Repository, threshold: float) -> List[DuplicationCluster]
- calculate_hash(code: str) -> str

Class: SimilarityGroup
Properties:
- similar_items: List[CodeElement]
- similarity_score: float
- common_pattern: str
```

#### `pattern_matcher.py`
```
Class: PatternMatcher
Responsibilities:
- Identify code patterns
- Match patterns across files
- Detect pattern evolution

Methods:
- extract_patterns(ast: AST) -> List[CodePattern]
- match_patterns(pattern: CodePattern, targets: List[AST]) -> List[PatternMatch]
- find_pattern_variance(matches: List[PatternMatch]) -> float
- detect_pattern_evolution(file_history: FileHistory) -> PatternEvolution

Class: CodePattern
Properties:
- pattern_type: str
- structure: Dict
- occurrences: List[PatternOccurrence]
- variance: float

Class: PatternMatch
Properties:
- pattern: CodePattern
- location: CodeLocation
- similarity: float
- differences: List[str]
```

### New Models

#### `coherence.py`
```
Class: PatternConsistencyReport
Properties:
- consistent_patterns: List[CodePattern]
- inconsistent_patterns: List[CodePattern]
- variance_score: float
- examples: List[InconsistencyExample]

Class: DriftEvent
Properties:
- timestamp: datetime
- files_affected: List[str]
- drift_type: str
- previous_pattern: CodePattern
- new_pattern: CodePattern
- severity: float

Class: DuplicationCluster
Properties:
- files: List[str]
- duplicated_code: str
- duplication_type: str
- similarity: float
- recommendation: str

Class: NamingReport
Properties:
- naming_conventions: Dict[str, List[str]]
- inconsistencies: List[NamingInconsistency]
- consistency_score: float

Class: NamingInconsistency
Properties:
- concept: str
- variations: List[str]
- locations: List[CodeLocation]
- suggested_standard: str

Class: CodeLocation
Properties:
- filepath: str
- line_start: int
- line_end: int
- function_name: Optional[str]
- class_name: Optional[str]
```

---

## Iteration 6: Prompt Engineering Insights

### New/Modified Packages
```
ai_collab_analyzer/
├── analyzers/
│   └── prompt_analyzer.py        # NEW
├── nlp/
│   ├── message_analyzer.py       # NEW
│   ├── sentiment_analyzer.py     # NEW
│   └── topic_extractor.py        # NEW
└── models/
    └── prompt_insights.py        # NEW
```

### New Analyzers

#### `prompt_analyzer.py`
```
Class: PromptAnalyzer(BaseAnalyzer)
Responsibilities:
- Analyze commit messages for prompt patterns
- Detect success/failure patterns
- Track learning curves
- Extract specifications evolution
- Measure prompt efficiency

Methods:
- analyze(repository: Repository) -> PromptAnalysisResult
- analyze_commit_messages(commits: List[Commit]) -> MessageAnalysis
- detect_success_patterns(repository: Repository) -> List[SuccessPattern]
- calculate_prompt_efficiency(repository: Repository) -> PromptEfficiencyMetrics
- track_learning_curve(repository: Repository) -> LearningCurve
- extract_specification_evolution(commits: List[Commit]) -> SpecificationEvolution

Class: PromptAnalysisResult
Properties:
- message_analysis: MessageAnalysis
- success_patterns: List[SuccessPattern]
- efficiency_metrics: PromptEfficiencyMetrics
- learning_curve: LearningCurve
- specification_evolution: SpecificationEvolution
- recommendations: List[str]
```

### New NLP Module

#### `message_analyzer.py`
```
Class: MessageAnalyzer
Responsibilities:
- Parse and analyze commit messages
- Extract intent and context
- Classify message types
- Track language evolution

Methods:
- analyze_message(message: str) -> MessageAnalysis
- classify_intent(message: str) -> Intent
- extract_keywords(message: str) -> List[str]
- detect_frustration_indicators(message: str) -> List[str]
- extract_constraints(message: str) -> List[str]

Class: MessageAnalysis
Properties:
- intent: Intent
- keywords: List[str]
- sentiment: float
- frustration_level: float
- clarity_score: float
- constraints_mentioned: List[str]

Enum: Intent
Values:
- FEATURE_ADD
- BUG_FIX
- REGENERATION
- CLARIFICATION
- CONSTRAINT_ADD
- REFACTOR
```

#### `sentiment_analyzer.py`
```
Class: SentimentAnalyzer
Responsibilities:
- Analyze sentiment in commit messages
- Detect frustration patterns
- Track emotional trends

Methods:
- analyze_sentiment(text: str) -> SentimentScore
- detect_frustration(text: str) -> float
- calculate_frustration_index(commits: List[Commit]) -> float
- track_sentiment_over_time(commits: List[Commit]) -> pd.DataFrame

Class: SentimentScore
Properties:
- polarity: float  # -1 to 1
- subjectivity: float  # 0 to 1
- confidence: float
```

#### `topic_extractor.py`
```
Class: TopicExtractor
Responsibilities:
- Extract topics from commit messages
- Track topic evolution
- Identify focus areas

Methods:
- extract_topics(messages: List[str], n_topics: int) -> List[Topic]
- track_topic_evolution(commits: List[Commit]) -> TopicEvolution
- identify_focus_shifts(topic_evolution: TopicEvolution) -> List[FocusShift]

Class: Topic
Properties:
- id: int
- keywords: List[str]
- weight: float
- related_commits: List[Commit]
```

### New Models

#### `prompt_insights.py`
```
Class: SuccessPattern
Properties:
- pattern_type: str
- commit_characteristics: Dict
- stability_score: float
- examples: List[Commit]
- recommendation: str

Class: PromptEfficiencyMetrics
Properties:
- first_time_success_rate: float
- average_iterations_to_stable: float
- regeneration_rate: float
- fix_rate: float
- efficiency_score: float
- efficiency_trend: List[Tuple[datetime, float]]

Class: LearningCurve
Properties:
- timeline: List[datetime]
- efficiency_over_time: List[float]
- improvement_rate: float
- plateau_points: List[datetime]
- skill_level: str  # beginner, intermediate, advanced

Class: SpecificationEvolution
Properties:
- timeline: List[SpecificationState]
- clarity_progression: List[float]
- constraint_accumulation: List[str]
- refinement_points: List[datetime]

Class: SpecificationState
Properties:
- timestamp: datetime
- requirements: List[str]
- constraints: List[str]
- clarity_score: float
- completeness_score: float

Class: FocusShift
Properties:
- timestamp: datetime
- from_topic: Topic
- to_topic: Topic
- reason: str
```

---

## Iteration 7: Predictive Analytics

### New/Modified Packages
```
ai_collab_analyzer/
├── analyzers/
│   └── predictive_analyzer.py    # NEW
├── ml/
│   ├── models/
│   │   ├── instability_predictor.py   # NEW
│   │   ├── cascade_predictor.py       # NEW
│   │   └── debt_forecaster.py         # NEW
│   ├── features/
│   │   └── feature_extractor.py       # NEW
│   └── training/
│       └── model_trainer.py           # NEW
└── models/
    └── predictions.py            # NEW
```

### New Analyzers

#### `predictive_analyzer.py`
```
Class: PredictiveAnalyzer(BaseAnalyzer)
Responsibilities:
- Predict future instability
- Forecast technical debt
- Calculate risk scores
- Generate early warnings

Methods:
- analyze(repository: Repository) -> PredictiveAnalysisResult
- predict_instability(repository: Repository) -> Dict[str, InstabilityPrediction]
- predict_fix_cascades(repository: Repository) -> List[CascadePrediction]
- forecast_technical_debt(repository: Repository) -> DebtForecast
- calculate_risk_scores(repository: Repository) -> Dict[str, RiskScore]
- generate_early_warnings(repository: Repository) -> List[Warning]

Class: PredictiveAnalysisResult
Properties:
- instability_predictions: Dict[str, InstabilityPrediction]
- cascade_predictions: List[CascadePrediction]
- debt_forecast: DebtForecast
- risk_scores: Dict[str, RiskScore]
- warnings: List[Warning]
- recommendations: List[PrioritizedRecommendation]
```

### New ML Module

#### `models/instability_predictor.py`
```
Class: InstabilityPredictor
Responsibilities:
- Train model to predict file instability
- Make predictions on new data
- Provide feature importance

Methods:
- __init__(model_type: str = "random_forest")
- train(training_data: pd.DataFrame, labels: pd.Series)
- predict(features: pd.DataFrame) -> np.ndarray
- predict_proba(features: pd.DataFrame) -> np.ndarray
- get_feature_importance() -> Dict[str, float]
- save_model(path: str)
- load_model(path: str)

Properties:
- model: sklearn model
- feature_names: List[str]
- trained: bool
```

#### `models/cascade_predictor.py`
```
Class: CascadePredictor
Responsibilities:
- Predict likelihood of fix cascades
- Estimate cascade impact
- Identify cascade triggers

Methods:
- predict_cascade_probability(file: str, repository: Repository) -> float
- predict_affected_files(file: str, repository: Repository) -> List[str]
- estimate_cascade_size(file: str, repository: Repository) -> int
- identify_triggers(repository: Repository) -> List[CascadeTrigger]
```

#### `models/debt_forecaster.py`
```
Class: DebtForecaster
Responsibilities:
- Forecast technical debt accumulation
- Predict debt hotspots
- Estimate debt resolution time

Methods:
- forecast_debt(repository: Repository, periods: int) -> DebtForecast
- predict_debt_hotspots(repository: Repository) -> List[DebtHotspot]
- estimate_resolution_time(debt: TechnicalDebt) -> timedelta
```

#### `features/feature_extractor.py`
```
Class: FeatureExtractor
Responsibilities:
- Extract features for ML models
- Engineer features from repository data
- Normalize and scale features

Methods:
- extract_file_features(file_history: FileHistory) -> pd.Series
- extract_commit_features(commit: Commit) -> pd.Series
- extract_temporal_features(commits: List[Commit]) -> pd.DataFrame
- engineer_features(repository: Repository) -> pd.DataFrame
- normalize_features(features: pd.DataFrame) -> pd.DataFrame

Extracted Features:
- Churn metrics
- Complexity trends
- Author diversity
- Temporal patterns
- Coupling density
- Fix ratio
- Age metrics
```

#### `training/model_trainer.py`
```
Class: ModelTrainer
Responsibilities:
- Train ML models on historical data
- Perform cross-validation
- Hyperparameter tuning
- Model evaluation

Methods:
- prepare_training_data(repository: Repository) -> Tuple[pd.DataFrame, pd.Series]
- train_model(model: BaseEstimator, X: pd.DataFrame, y: pd.Series) -> BaseEstimator
- cross_validate(model: BaseEstimator, X: pd.DataFrame, y: pd.Series) -> Dict
- tune_hyperparameters(model: BaseEstimator, X: pd.DataFrame, y: pd.Series) -> BaseEstimator
- evaluate_model(model: BaseEstimator, X_test: pd.DataFrame, y_test: pd.Series) -> Dict
```

### New Models

#### `predictions.py`
```
Class: InstabilityPrediction
Properties:
- file: str
- probability: float
- confidence: float
- predicted_next_issue: Optional[datetime]
- contributing_factors: List[str]
- recommendation: str

Class: CascadePrediction
Properties:
- trigger_file: str
- probability: float
- estimated_affected_files: List[str]
- estimated_cascade_size: int
- risk_level: str
- mitigation_suggestions: List[str]

Class: DebtForecast
Properties:
- timeline: List[datetime]
- forecasted_debt: List[float]
- debt_hotspots: List[DebtHotspot]
- trend: str  # increasing, stable, decreasing
- confidence_interval: Tuple[float, float]

Class: DebtHotspot
Properties:
- location: str
- current_debt: float
- forecasted_debt: float
- growth_rate: float
- priority: int

Class: RiskScore
Properties:
- entity: str  # file, module, or feature
- score: float  # 0-100
- risk_level: str  # low, medium, high, critical
- factors: List[RiskFactor]
- trend: str

Class: RiskFactor
Properties:
- name: str
- contribution: float
- description: str

Class: Warning
Properties:
- severity: str
- message: str
- affected_files: List[str]
- predicted_impact: str
- recommended_action: str
- deadline: Optional[datetime]

Class: PrioritizedRecommendation
Properties:
- priority: int
- action: str
- rationale: str
- expected_impact: str
- effort_estimate: str
- affected_areas: List[str]
```

---

## Iteration 8: Interactive Dashboard & Real-time Monitoring

### New/Modified Packages
```
ai_collab_analyzer/
├── web/
│   ├── api/
│   │   ├── app.py                # NEW
│   │   ├── routes/
│   │   │   ├── analysis.py       # NEW
│   │   │   ├── repository.py     # NEW
│   │   │   └── export.py         # NEW
│   │   └── middleware/
│   │       ├── auth.py           # NEW
│   │       └── cache.py          # NEW
│   ├── frontend/
│   │   ├── components/
│   │   │   ├── Dashboard.jsx     # NEW (if React)
│   │   │   ├── Timeline.jsx      # NEW
│   │   │   └── FileExplorer.jsx  # NEW
│   │   └── pages/
│   │       ├── overview.py       # NEW (if Streamlit)
│   │       └── details.py        # NEW
│   └── websocket/
│       └── realtime.py           # NEW
├── storage/
│   ├── database.py               # NEW
│   ├── models.py                 # NEW (DB models)
│   └── migrations/               # NEW
└── scheduler/
    └── analysis_scheduler.py     # NEW
```

### Web API Module

#### `api/app.py`
```
Class: AnalyzerAPI
Responsibilities:
- FastAPI application setup
- Route configuration
- Middleware setup
- WebSocket management

Methods:
- create_app() -> FastAPI
- setup_routes(app: FastAPI)
- setup_middleware(app: FastAPI)
- setup_cors(app: FastAPI)
```

#### `api/routes/analysis.py`
```
Endpoints:
- POST /api/analyze - Trigger new analysis
- GET /api/analysis/{id} - Get analysis results
- GET /api/analysis/{id}/status - Get analysis status
- GET /api/repositories - List analyzed repositories
- GET /api/repositories/{id}/metrics - Get specific metrics
- GET /api/repositories/{id}/timeline - Get timeline data
- POST /api/repositories/{id}/refresh - Refresh analysis

Class: AnalysisController
Methods:
- trigger_analysis(repo_path: str, config: AnalysisConfig) -> str
- get_analysis_result(analysis_id: str) -> AnalysisResult
- get_analysis_status(analysis_id: str) -> AnalysisStatus
```

#### `api/routes/repository.py`
```
Endpoints:
- GET /api/repositories - List repositories
- POST /api/repositories - Add repository
- GET /api/repositories/{id} - Get repository details
- DELETE /api/repositories/{id} - Remove repository
- GET /api/repositories/{id}/files - List files
- GET /api/repositories/{id}/files/{path} - Get file details

Class: RepositoryController
Methods:
- list_repositories() -> List[RepositoryInfo]
- add_repository(url: str, path: str) -> RepositoryInfo
- get_repository(repo_id: str) -> RepositoryInfo
- delete_repository(repo_id: str)
```

#### `api/routes/export.py`
```
Endpoints:
- GET /api/export/report/{id}/html - Export HTML report
- GET /api/export/report/{id}/pdf - Export PDF report
- GET /api/export/report/{id}/json - Export JSON data
- GET /api/export/metrics/{id}/csv - Export metrics as CSV

Class: ExportController
Methods:
- export_html(analysis_id: str) -> Response
- export_pdf(analysis_id: str) -> Response
- export_json(analysis_id: str) -> Response
- export_csv(analysis_id: str, metric_type: str) -> Response
```

### Storage Module

#### `storage/database.py`
```
Class: DatabaseManager
Responsibilities:
- Database connection management
- Query execution
- Transaction management
- Connection pooling

Methods:
- __init__(connection_string: str)
- get_session() -> Session
- execute_query(query: str, params: Dict) -> List
- save_analysis_result(result: AnalysisResult) -> str
- get_analysis_result(analysis_id: str) -> AnalysisResult
- list_repositories() -> List[Repository]
- cleanup_old_data(days: int)
```

#### `storage/models.py`
```
SQLAlchemy Models:

Class: RepositoryModel (Table: repositories)
Columns:
- id: UUID (PK)
- name: str
- path: str
- url: str
- created_at: datetime
- last_analyzed: datetime
- status: str

Class: AnalysisModel (Table: analyses)
Columns:
- id: UUID (PK)
- repository_id: UUID (FK)
- analysis_type: str
- status: str
- started_at: datetime
- completed_at: datetime
- result_data: JSON

Class: MetricModel (Table: metrics)
Columns:
- id: UUID (PK)
- analysis_id: UUID (FK)
- metric_name: str
- metric_value: float
- metadata: JSON
- timestamp: datetime

Class: FileHistoryModel (Table: file_histories)
Columns:
- id: UUID (PK)
- repository_id: UUID (FK)
- filepath: str
- first_seen: datetime
- last_modified: datetime
- total_changes: int
- metrics: JSON
```

### WebSocket Module

#### `websocket/realtime.py`
```
Class: RealtimeManager
Responsibilities:
- Manage WebSocket connections
- Push real-time updates
- Handle subscriptions

Methods:
- connect(websocket: WebSocket, client_id: str)
- disconnect(client_id: str)
- broadcast_update(message: dict)
- send_to_client(client_id: str, message: dict)
- subscribe_to_analysis(client_id: str, analysis_id: str)
```

### Scheduler Module

#### `scheduler/analysis_scheduler.py`
```
Class: AnalysisScheduler
Responsibilities:
- Schedule periodic analyses
- Manage analysis queue
- Handle analysis lifecycle

Methods:
- schedule_analysis(repo_id: str, schedule: str)  # cron format
- cancel_scheduled_analysis(schedule_id: str)
- run_scheduled_analyses()
- queue_analysis(repo_id: str, priority: int)
- process_queue()

Class: AnalysisQueue
Responsibilities:
- FIFO queue for analysis jobs
- Priority management
- Job status tracking

Methods:
- enqueue(job: AnalysisJob)
- dequeue() -> AnalysisJob
- get_status(job_id: str) -> JobStatus
- cancel_job(job_id: str)
```

### Frontend Components (Streamlit Example)

#### `frontend/pages/overview.py`
```
Function: render_overview_page()
Responsibilities:
- Display repository overview
- Show key metrics
- Present health scores
- Link to detailed views

Components:
- Repository selector
- Health score card
- Metrics summary
- Timeline chart
- Hotspot table
- Quick actions
```

#### `frontend/pages/details.py`
```
Function: render_details_page()
Responsibilities:
- Show detailed analysis results
- Interactive visualizations
- File-level drill-down
- Export options

Components:
- File explorer
- Metric charts
- Coupling graph
- Timeline visualization
- Prediction panels
- Export buttons
```

### Modified Core Components

#### `core/repository.py` (Enhanced)
```
# Add methods for database integration:
- save_to_database(db: DatabaseManager)
- load_from_database(db: DatabaseManager, repo_id: str)
- update_status(status: str)
```

#### `reporters/html_reporter.py` (Enhanced)
```
# Add methods:
- generate_interactive_report() -> str
- generate_dashboard_data() -> Dict
```

---

## Iteration 9: Multi-Repository & Benchmarking

### New/Modified Packages
```
ai_collab_analyzer/
├── multi_repo/
│   ├── aggregator.py             # NEW
│   ├── comparator.py             # NEW
│   └── portfolio_manager.py      # NEW
├── benchmarking/
│   ├── benchmark_db.py           # NEW
│   ├── benchmark_calculator.py   # NEW
│   └── trend_analyzer.py         # NEW
└── models/
    └── benchmarks.py             # NEW
```

### Multi-Repo Module

#### `multi_repo/aggregator.py`
```
Class: MultiRepoAggregator
Responsibilities:
- Aggregate metrics across repositories
- Calculate portfolio-level statistics
- Identify cross-repo patterns

Methods:
- aggregate_repositories(repo_ids: List[str]) -> AggregatedMetrics
- calculate_portfolio_health(repos: List[Repository]) -> PortfolioHealth
- identify_common_patterns(repos: List[Repository]) -> List[CrossRepoPattern]
- aggregate_by_dimension(repos: List[Repository], dimension: str) -> Dict

Class: AggregatedMetrics
Properties:
- total_repositories: int
- total_commits: int
- average_health_score: float
- aggregated_metrics: Dict[str, float]
- distribution_stats: Dict[str, StatisticalSummary]
```

#### `multi_repo/comparator.py`
```
Class: RepositoryComparator
Responsibilities:
- Compare repositories against each other
- Rank repositories by metrics
- Identify outliers
- Generate comparison reports

Methods:
- compare_repositories(repo_ids: List[str]) -> ComparisonResult
- rank_by_metric(repos: List[Repository], metric: str) -> List[RankedRepo]
- identify_outliers(repos: List[Repository]) -> List[OutlierRepo]
- generate_comparison_matrix(repos: List[Repository]) -> pd.DataFrame

Class: ComparisonResult
Properties:
- repositories: List[Repository]
- comparison_matrix: pd.DataFrame
- rankings: Dict[str, List[RankedRepo]]
- outliers: List[OutlierRepo]
- insights: List[str]
```

#### `multi_repo/portfolio_manager.py`
```
Class: PortfolioManager
Responsibilities:
- Manage collection of repositories
- Track portfolio-level metrics
- Generate portfolio reports
- Monitor portfolio health

Methods:
- add_repository(repo: Repository)
- remove_repository(repo_id: str)
- get_portfolio_summary() -> PortfolioSummary
- get_health_trends() -> pd.DataFrame
- identify_risk_areas() -> List[RiskArea]
- generate_portfolio_report() -> PortfolioReport

Class: PortfolioSummary
Properties:
- total_projects: int
- healthy_projects: int
- at_risk_projects: int
- critical_projects: int
- overall_health_score: float
- key_metrics: Dict[str, float]
- trends: Dict[str, Trend]
```

### Benchmarking Module

#### `benchmarking/benchmark_db.py`
```
Class: BenchmarkDatabase
Responsibilities:
- Store anonymized benchmark data
- Retrieve comparative statistics
- Manage benchmark datasets
- Ensure privacy

Methods:
- store_benchmark(repo_metrics: Dict, metadata: Dict) -> str
- get_benchmark_stats(filters: Dict) -> BenchmarkStats
- get_percentile(metric: str, value: float, filters: Dict) -> float
- get_industry_trends(metric: str, period: str) -> pd.DataFrame
- anonymize_data(data: Dict) -> Dict

Class: BenchmarkStats
Properties:
- metric_name: str
- mean: float
- median: float
- std_dev: float
- percentiles: Dict[int, float]  # 25, 50, 75, 90, 95, 99
- sample_size: int
- filters_applied: Dict
```

#### `benchmarking/benchmark_calculator.py`
```
Class: BenchmarkCalculator
Responsibilities:
- Calculate relative performance
- Generate benchmark comparisons
- Identify best practices
- Score against benchmarks

Methods:
- calculate_relative_performance(repo: Repository, benchmark: BenchmarkStats) -> RelativePerformance
- generate_benchmark_report(repo: Repository) -> BenchmarkReport
- identify_best_practices(top_performers: List[Repository]) -> List[BestPractice]
- score_against_industry(repo: Repository) -> IndustryScore

Class: RelativePerformance
Properties:
- metric: str
- repo_value: float
- benchmark_median: float
- percentile: float
- performance_level: str  # below_average, average, above_average, excellent
- gap_to_median: float
```

#### `benchmarking/trend_analyzer.py`
```
Class: TrendAnalyzer
Responsibilities:
- Analyze trends over time
- Identify improvement patterns
- Forecast future trends
- Compare organizational progress

Methods:
- analyze_trend(metric: str, time_series: pd.Series) -> Trend
- identify_improvement_patterns(repos: List[Repository]) -> List[ImprovementPattern]
- forecast_trend(historical_data: pd.DataFrame, periods: int) -> Forecast
- compare_organizational_trends(org_data: Dict, industry_data: Dict) -> TrendComparison

Class: Trend
Properties:
- metric: str
- direction: str  # increasing, decreasing, stable
- rate_of_change: float
- significance: float
- forecast: Optional[Forecast]
```

### New Models

#### `benchmarks.py`
```
Class: BenchmarkReport
Properties:
- repository: Repository
- benchmark_date: datetime
- relative_performance: Dict[str, RelativePerformance]
- industry_comparison: IndustryComparison
- best_practices: List[BestPractice]
- improvement_opportunities: List[ImprovementOpportunity]

Class: IndustryComparison
Properties:
- industry: str
- repo_score: float
- industry_median: float
- industry_top_10_percent: float
- rank_estimate: str
- key_differences: List[str]

Class: BestPractice
Properties:
- practice: str
- description: str
- evidence: List[str]
- repos_following: int
- impact: str
- adoption_difficulty: str

Class: ImprovementOpportunity
Properties:
- area: str
- current_state: str
- target_state: str
- gap: float
- priority: int
- estimated_effort: str
- expected_benefit: str

Class: CrossRepoPattern
Properties:
- pattern_type: str
- occurrences: int
- affected_repos: List[str]
- common_characteristics: Dict
- recommendations: List[str]

Class: PortfolioHealth
Properties:
- health_score: float
- health_distribution: Dict[str, int]  # healthy, at_risk, critical
- top_risks: List[RiskArea]
- top_performers: List[str]
- improvement_trajectory: Trend

Class: RiskArea
Properties:
- area: str
- affected_repos: List[str]
- risk_level: str
- description: str
- mitigation_strategy: str
```

### Enhanced Storage

#### `storage/models.py` (Enhanced)
```
# Add new tables:

Class: BenchmarkDataModel (Table: benchmark_data)
Columns:
- id: UUID (PK)
- anonymous_id: str
- metrics: JSON
- metadata: JSON
- created_at: datetime
- industry: str
- team_size: int

Class: PortfolioModel (Table: portfolios)
Columns:
- id: UUID (PK)
- name: str
- description: str
- owner: str
- repositories: List[UUID]
- created_at: datetime
```

---

## Iteration 10: AI Integration & Recommendations Engine

### New/Modified Packages
```
ai_collab_analyzer/
├── ai/
│   ├── assistant.py              # NEW
│   ├── recommendation_engine.py  # NEW
│   ├── prompt_generator.py       # NEW
│   └── query_processor.py        # NEW
├── integrations/
│   ├── ci_cd/
│   │   ├── github_actions.py     # NEW
│   │   └── gitlab_ci.py          # NEW
│   ├── issue_trackers/
│   │   ├── jira.py               # NEW
│   │   └── github_issues.py      # NEW
│   └── code_review/
│       └── pr_analyzer.py        # NEW
├── feedback/
│   └── feedback_tracker.py       # NEW
└── rules/
    └── rule_engine.py            # NEW
```

### AI Module

#### `ai/assistant.py`
```
Class: AIAssistant
Responsibilities:
- Provide conversational interface to analysis
- Answer natural language queries
- Generate insights and summaries
- Explain findings in context

Methods:
- ask(question: str, context: AnalysisContext) -> AssistantResponse
- explain_metric(metric: str, value: float, context: AnalysisContext) -> str
- summarize_analysis(analysis: AnalysisResult) -> str
- suggest_next_steps(repository: Repository) -> List[Suggestion]
- generate_meeting_summary(analysis: AnalysisResult, audience: str) -> str

Class: AssistantResponse
Properties:
- answer: str
- confidence: float
- supporting_data: Dict
- visualizations: List[str]
- follow_up_questions: List[str]
- references: List[Reference]

Class: AnalysisContext
Properties:
- repository: Repository
- analysis_results: List[AnalysisResult]
- user_role: str
- previous_queries: List[str]
```

#### `ai/recommendation_engine.py`
```
Class: RecommendationEngine
Responsibilities:
- Generate actionable recommendations
- Prioritize recommendations
- Learn from feedback
- Adapt to project context

Methods:
- generate_recommendations(repository: Repository) -> List[Recommendation]
- prioritize_recommendations(recommendations: List[Recommendation]) -> List[Recommendation]
- get_contextual_recommendations(context: ProjectContext) -> List[Recommendation]
- learn_from_feedback(recommendation_id: str, feedback: Feedback)
- get_recommendation_history(repo_id: str) -> List[RecommendationWithOutcome]

Class: Recommendation
Properties:
- id: str
- type: str  # refactor, prompt_improve, architecture, process
- title: str
- description: str
- rationale: str
- priority: int
- effort_estimate: str
- expected_impact: str
- implementation_steps: List[str]
- relevant_files: List[str]
- relevant_metrics: Dict[str, float]
- success_criteria: List[str]

Class: ProjectContext
Properties:
- repository: Repository
- team_size: int
- project_phase: str
- main_languages: List[str]
- ai_tools_used: List[str]
- pain_points: List[str]
```

#### `ai/prompt_generator.py`
```
Class: PromptGenerator
Responsibilities:
- Generate optimized prompts for AI tools
- Learn from successful patterns
- Adapt to project context
- Provide prompt templates

Methods:
- generate_prompt(task: str, context: Dict) -> GeneratedPrompt
- create_template(pattern: SuccessPattern) -> PromptTemplate
- suggest_improvements(current_prompt: str, results: Dict) -> List[str]
- get_templates_for_context(context: ProjectContext) -> List[PromptTemplate]

Class: GeneratedPrompt
Properties:
- prompt_text: str
- context_included: List[str]
- constraints: List[str]
- expected_output: str
- tips: List[str]
- based_on_pattern: Optional[SuccessPattern]

Class: PromptTemplate
Properties:
- id: str
- name: str
- template: str
- variables: List[str]
- use_case: str
- success_rate: float
- example: str
```

#### `ai/query_processor.py`
```
Class: QueryProcessor
Responsibilities:
- Parse natural language queries
- Map queries to analysis functions
- Extract query intent and parameters
- Handle multi-step queries

Methods:
- process_query(query: str, context: AnalysisContext) -> QueryPlan
- extract_intent(query: str) -> Intent
- extract_entities(query: str) -> List[Entity]
- decompose_complex_query(query: str) -> List[SubQuery]
- execute_query_plan(plan: QueryPlan) -> QueryResult

Class: QueryPlan
Properties:
- original_query: str
- intent: Intent
- required_analyses: List[str]
- filters: Dict
- aggregations: List[str]
- visualization_type: Optional[str]

Class: QueryResult
Properties:
- answer: str
- data: Dict
- visualizations: List[Figure]
- confidence: float
- explanation: str
```

### Integrations Module

#### `integrations/ci_cd/github_actions.py`
```
Class: GitHubActionsIntegration
Responsibilities:
- Integrate with GitHub Actions
- Trigger analysis on events
- Post results to PRs
- Update check status

Methods:
- setup_workflow(repo_url: str) -> str
- trigger_on_push(repo_id: str, commit_sha: str)
- trigger_on_pr(repo_id: str, pr_number: int)
- post_results_to_pr(pr_number: int, results: AnalysisResult)
- update_check_status(commit_sha: str, status: CheckStatus)

Class: CheckStatus
Properties:
- state: str  # pending, success, failure
- description: str
- details_url: str
- metrics: Dict[str, float]
```

#### `integrations/issue_trackers/jira.py`
```
Class: JiraIntegration
Responsibilities:
- Create issues from findings
- Link analysis to existing issues
- Update issue status
- Track recommendations

Methods:
- create_issue(finding: Finding) -> str
- link_to_issue(issue_id: str, finding: Finding)
- update_issue_with_analysis(issue_id: str, analysis: AnalysisResult)
- track_recommendation(recommendation: Recommendation) -> str
- get_issue_status(issue_id: str) -> IssueStatus
```

#### `integrations/code_review/pr_analyzer.py`
```
Class: PRAnalyzer
Responsibilities:
- Analyze pull requests
- Flag anti-patterns in PRs
- Suggest improvements
- Predict PR risks

Methods:
- analyze_pr(pr_data: PullRequest) -> PRAnalysis
- check_for_antipatterns(pr_data: PullRequest) -> List[AntiPattern]
- predict_pr_risk(pr_data: PullRequest) -> RiskAssessment
- generate_review_comment(finding: Finding) -> str

Class: PRAnalysis
Properties:
- pr_number: int
- risk_score: float
- antipatterns: List[AntiPattern]
- size_assessment: str
- coupling_impact: List[str]
- recommended_reviewers: List[str]
- estimated_review_time: timedelta
```

### Feedback Module

#### `feedback/feedback_tracker.py`
```
Class: FeedbackTracker
Responsibilities:
- Collect user feedback
- Track recommendation outcomes
- Learn from user interactions
- Improve recommendations over time

Methods:
- record_feedback(recommendation_id: str, feedback: Feedback)
- get_recommendation_effectiveness(recommendation_id: str) -> float
- analyze_feedback_patterns() -> FeedbackAnalysis
- update_recommendation_weights(feedback_data: List[Feedback])

Class: Feedback
Properties:
- recommendation_id: str
- user_id: str
- rating: int  # 1-5
- was_helpful: bool
- was_implemented: bool
- outcome: Optional[str]
- comments: str
- timestamp: datetime

Class: FeedbackAnalysis
Properties:
- total_feedback: int
- average_rating: float
- implementation_rate: float
- effectiveness_by_type: Dict[str, float]
- user_satisfaction: float
- improvement_areas: List[str]
```

### Rules Module

#### `rules/rule_engine.py`
```
Class: RuleEngine
Responsibilities:
- Define custom quality rules
- Evaluate rules against repository
- Generate alerts for violations
- Support user-defined rules

Methods:
- add_rule(rule: Rule)
- remove_rule(rule_id: str)
- evaluate_rules(repository: Repository) -> List[RuleViolation]
- get_active_rules() -> List[Rule]
- import_rules(config_file: str)

Class: Rule
Properties:
- id: str
- name: str
- description: str
- condition: Callable
- severity: str
- message_template: str
- auto_fix: Optional[Callable]

Class: RuleViolation
Properties:
- rule: Rule
- severity: str
- message: str
- location: str
- suggestion: str
- auto_fixable: bool

Example Rules:
- "Hotspot files must have test coverage > 80%"
- "Files changed more than 10 times in 7 days require review"
- "AI-generated code must be reviewed within 24 hours"
- "Coupling strength between modules must be < 0.5"
```

### Enhanced API Routes

#### `api/routes/ai.py` (NEW)
```
Endpoints:
- POST /api/ai/ask - Ask AI assistant a question
- GET /api/ai/recommendations - Get recommendations for repository
- POST /api/ai/recommendations/{id}/feedback - Submit feedback
- GET /api/ai/prompts - Get prompt templates
- POST /api/ai/prompts/generate - Generate custom prompt
- GET /api/ai/summary - Get AI-generated summary

Class: AIController
Methods:
- ask_question(question: str, repo_id: str) -> AssistantResponse
- get_recommendations(repo_id: str, filters: Dict) -> List[Recommendation]
- submit_feedback(recommendation_id: str, feedback: Feedback)
- generate_prompt(task: str, context: Dict) -> GeneratedPrompt
```

### Enhanced Storage

#### `storage/models.py` (Enhanced)
```
# Add new tables:

Class: RecommendationModel (Table: recommendations)
Columns:
- id: UUID (PK)
- repository_id: UUID (FK)
- type: str
- title: str
- description: str
- priority: int
- status: str
- created_at: datetime
- implemented_at: datetime
- outcome: str

Class: FeedbackModel (Table: feedback)
Columns:
- id: UUID (PK)
- recommendation_id: UUID (FK)
- user_id: str
- rating: int
- was_helpful: bool
- was_implemented: bool
- comments: str
- timestamp: datetime

Class: RuleModel (Table: custom_rules)
Columns:
- id: UUID (PK)
- repository_id: UUID (FK)
- name: str
- condition: str  # serialized
- severity: str
- active: bool
- created_at: datetime

Class: QueryHistoryModel (Table: query_history)
Columns:
- id: UUID (PK)
- user_id: str
- query: str
- response: str
- confidence: float
- helpful: bool
- timestamp: datetime
```

---

## Cross-Cutting Concerns (All Iterations)

### Configuration Management
```
Class: Config
Responsibilities:
- Load configuration from files/env
- Provide configuration to components
- Validate configuration

Properties:
- database_url: str
- cache_settings: Dict
- analysis_settings: Dict
- api_settings: Dict
- ai_settings: Dict
```

### Logging
```
Class: Logger
Responsibilities:
- Structured logging
- Log levels
- Context enrichment

Methods:
- info(message: str, context: Dict)
- warning(message: str, context: Dict)
- error(message: str, error: Exception, context: Dict)
```

### Caching
```
Class: CacheManager
Responsibilities:
- Cache expensive computations
- Invalidate stale cache
- Distributed caching support

Methods:
- get(key: str) -> Optional[Any]
- set(key: str, value: Any, ttl: int)
- invalidate(pattern: str)
```

### Testing Support
```
Class: TestDataGenerator
Responsibilities:
- Generate test repositories
- Create mock data
- Support unit/integration tests

Methods:
- create_test_repository() -> Repository
- generate_commits(count: int) -> List[Commit]
- create_analysis_result() -> AnalysisResult
```

---

## Architecture Evolution Summary

| Iteration | New Modules | New Classes | Total Classes (Cumulative) |
|-----------|-------------|-------------|---------------------------|
| 1 | 6 | 12 | 12 |
| 2 | 3 | 8 | 20 |
| 3 | 4 | 10 | 30 |
| 4 | 3 | 9 | 39 |
| 5 | 4 | 12 | 51 |
| 6 | 3 | 11 | 62 |
| 7 | 4 | 14 | 76 |
| 8 | 6 | 18 | 94 |
| 9 | 3 | 12 | 106 |
| 10 | 5 | 20 | 126 |

Each iteration maintains backward compatibility while adding new capabilities through:
- Interface-based design (BaseAnalyzer)
- Plugin architecture (analyzers are independent)
- Layered separation (data, analysis, presentation)
- Database-backed persistence (from Iteration 8)
- API-based access (from Iteration 8)