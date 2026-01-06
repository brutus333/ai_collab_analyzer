# Agent Specification: Human-AI Collaboration Pattern Analyzer
## Purpose
Analyze version control history and development artifacts from AI-assisted projects to identify collaboration patterns, inefficiencies, friction points, and opportunities for improvement in the human-AI development workflow.
## Core Objectives

- Map the collaboration landscape - understand how humans and AI interact throughout the development lifecycle
- Identify friction points - find where the collaboration breaks down or becomes inefficient
- Detect patterns of success and failure - learn what works and what doesn't in human-AI pairing
- Provide actionable insights - guide developers on how to improve their AI collaboration strategy

## Data Sources
### Primary Sources

- Git repository history - commits, diffs, blame data, branch patterns
- Commit messages - natural language indicating intent, frustration, fixes
- File change patterns - creation, modification, deletion timelines
- Code content - the actual code at different points in time

### Secondary Sources (if available)

- Prompt logs - what was asked of the AI and when
- Chat transcripts - conversations with AI coding assistants
- Issue/ticket tracking - problems reported, feature requests
- Documentation changes - specs, READMEs, architectural decisions
- Test results - pass/fail patterns over time
- IDE/editor metadata - if available, manual edits vs AI suggestions

## Key Analysis Dimensions
### 1. Generation Patterns

- Initial generation quality - how often does first AI output survive unchanged?
- Regeneration frequency - files recreated multiple times vs incrementally refined
- Generation burst patterns - large AI generations followed by many small human fixes
- Generation abandonment - AI-generated code completely replaced by human rewrites

### 2. Human Intervention Signatures

Edit types:

- Bug fixes (syntax errors, logic errors, runtime errors)
- Refinements (optimization, style improvements)
- Structural changes (refactoring, architectural modifications)
- Integration work (connecting AI-generated modules)
- Cleanup (removing hallucinated imports, fixing inconsistencies)

- Intervention timing - immediate vs delayed fixes
- Intervention intensity - minor tweaks vs major overhauls
- Intervention patterns - same issues fixed repeatedly

### 3. Temporal Coupling Analysis (Modified for AI)

- Prompt-related coupling - files likely generated together in same prompt session
- Fix cascades - one fix triggering fixes in related files
- Regeneration coupling - files regenerated together repeatedly
- Stability correlation - files that stabilize together

### 4. Architectural Coherence

- Pattern consistency - does similar code follow similar patterns across the project?
- API compatibility - do AI-generated modules interface cleanly?
- Design drift - architectural decisions changing over time/regenerations
- Naming inconsistencies - similar concepts named differently across files
- Duplication patterns - same functionality implemented multiple times differently

### 5. Knowledge Boundaries

- AI capability map - what types of code stabilize quickly vs require heavy human intervention?
- Domain complexity indicators - where does the AI struggle with project-specific logic?
- Context window effects - problems arising from AI losing track of broader context
- Hallucination zones - consistent areas where AI generates non-existent APIs, libraries, or patterns

### 6. Prompt Engineering Evolution

- Commit message analysis - detecting frustration, clarification, constraint-adding language
- Specification refinement patterns - how requirements get clearer over iterations
- Constraint accumulation - growing lists of "don't do X" or "make sure to Y"
- Success pattern extraction - what commit messages correlate with stable code?

## Output Metrics & Visualizations
### Quantitative Metrics

- Stability Score - time/iterations until file stops changing (per file, per module)
- Human Touch Ratio - proportion of code ultimately modified by humans
- Regeneration Cost - how many regenerations per stable file
- Fix Frequency - human fixes per AI generation
- Coherence Score - consistency of patterns across codebase
- Prompt Efficiency - ratio of useful output to total generations

### Qualitative Indicators

- Friction Hotspots - files/modules with highest human intervention
- AI Strength Zones - where AI performs well consistently
- Collaboration Anti-patterns - repeated failure modes
- Evolution Narrative - how project development approach changed over time

### Visualization Types

- Temporal Heatmaps - activity patterns over time showing generation/fix cycles
- Dependency Graphs - showing temporal coupling and regeneration cascades
- Stability Timelines - when different modules reached stability
- Intervention Maps - spatial/architectural view of where humans intervene most
- Pattern Drift Diagrams - how architectural decisions evolved/diverged
- Prompt Archaeology Timeline - reconstruction of likely prompting strategy evolution

## Analysis Workflows
### 1. Initial Repository Scan

- Clone and index repository
- Parse all commits chronologically
- Build file evolution graph
- Identify potential AI-generated vs human-written code patterns

### 2. Pattern Detection

- Statistical analysis of commit patterns
- Code similarity analysis across time
- Linguistic analysis of commit messages
- Change velocity analysis

### 3. Collaboration Reconstruction

- Infer generation sessions from commit timing/size
- Identify fix cycles following generations
- Map human intervention patterns
- Detect regeneration vs refinement approaches

### 4. Insight Generation

- Identify top friction points
- Recommend workflow improvements
- Suggest areas for better prompting
- Highlight successful patterns to replicate

### 5. Report Generation

- Executive summary
- Detailed findings by category
- Visualizations
- Actionable recommendations
- Best practices extracted from successful patterns

### Heuristics for Detecting AI vs Human Code
Since explicit labeling may not exist:

- Commit size patterns - large commits with many new files suggest AI generation
- Commit message style - "Add X feature" vs "Fix bug in X" vs "Regenerate X with corrections"
- Code style consistency - AI often maintains perfect style within generation, humans vary
- Completeness patterns - AI tends to generate complete files, humans make partial edits
- Error patterns - certain bugs are AI-typical (hallucinated imports, type inconsistencies)
- Timestamp clustering - rapid successive commits suggest fix cycles after AI generation
- Documentation completeness - AI often generates comprehensive docstrings initially

## Configuration Options
### Analysis Depth

- Quick scan (surface metrics only)
- Standard analysis (all core metrics)
- Deep analysis (includes semantic code analysis, detailed pattern detection)

### Focus Areas

- Specific file types or modules
- Time ranges
- Specific developers/contributors
- Particular technologies or frameworks

### Thresholds

- Minimum file change frequency to be considered "hotspot"
- Stability definition (days/commits without change)
- Similarity thresholds for pattern detection

### Output Formats

- Interactive Dashboard - web-based exploration of findings
- Static Report - PDF/HTML comprehensive analysis
- JSON/CSV Data Export - raw metrics for further analysis
- Integration Alerts - flags for CI/CD if concerning patterns detected

### Privacy & Ethics Considerations

- Analyze patterns, not personal performance metrics
- Focus on workflow improvement, not developer evaluation
- Aggregate data when showing team patterns
- Option to anonymize contributor information
- Clear distinction between descriptive analysis and prescriptive judgment

### Success Criteria

The agent is successful if it can:

- Accurately identify friction points in human-AI collaboration
- Provide insights that lead to measurable workflow improvements
- Help teams understand their AI collaboration patterns
- Reduce regeneration cycles and human intervention needs over time
- Inform better prompt engineering strategies

## Future Extensions

- Real-time monitoring - analyze as development happens
- Predictive alerts - warn when anti-patterns emerge
- Prompt recommendation - suggest better prompting strategies
- Integration with AI tools - direct feedback to improve AI outputs
- Cross-project learning - patterns from multiple projects
- Benchmarking - compare against similar projects


This agent would essentially create a new discipline: Collaborative Forensics for human-AI software development.