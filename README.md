# AI Collaboration Pattern Analyzer

Analyze version control history and development artifacts to identify collaboration patterns, inefficiencies, and improvement opportunities in human-AI development workflows.

## Features

- **Repository Health Scanning**: Churn rate, commit frequency, and hotspot identification.
- **Collaboration Pattern Detection**:
  - **Bursts**: Detecting rapid, low-interval activity phases.
  - **Regenerations**: Identifying files that are frequently rewritten (suspected AI regeneration cycles).
- **Collaboration Graph**: Visualizing temporal coupling (files that change together) using NetworkX.
- **Instructional Correlation**: Correlating imperative changes in documentation (agent instructions) with improvements in code stability and first-time success rates.
- **Prompt Engineering Evolution**: Automatically extracting AI prompts and instructions from code comments, commit messages, and documentation files (`.md`, `.txt`).
- **Interactive Reports & Dashboard**: Generate self-contained HTML reports or use the real-time Streamlit dashboard for deep-dive analysis.

## Installation

```bash
# Clone the repository
git clone <repo-url>
cd ai_collab_analyzer

# Install dependencies using Poetry
poetry install
```

## Usage

### Analyze a Repository

```bash
python -m ai_collab_analyzer.cli analyze /path/to/your/repo --output report.html
```

### Interactive Dashboard

The project includes a Streamlit-based dashboard for exploring cross-repository metrics and deep-diving into specific patterns.

#### 1. Start the API Server
The dashboard requires the backend API to be running:
```bash
python -m uvicorn ai_collab_analyzer.web.api.app:app --port 8000
```

#### 2. Start the Streamlit Dashboard
```bash
python -m streamlit run ai_collab_analyzer/web/dashboard/app.py
```

### Options

- `path`: (Required) Path to the local git repository.
- `--output`, `-o`: (Optional) Path to the generated HTML report (default: `report.html`).

## Development

### Running Tests

```bash
python -m pytest
```

### Architecture

- `core/`: Data models (Commit, FileHistory, Repository).
- `extractors/`: Data extraction logic (GitExtractor using PyDriller).
- `analyzers/`: Domain-specific analysis (Health, Pattern, Coupling, Prompt).
- `metrics/`: Core metric calculations (Churn, Fix Ratio).
- `visualizers/`: Plotly chart builders.
- `reporters/`: HTML report generation.

## Acknowledgements & Legal Considerations

This tool was inspired by techniques described in Adam Tornhill's **"Your Code as a Crime Scene"**, adapted and extended for analyzing human-AI collaboration patterns in software development.

### Academic Foundation
The analysis methods used in this project are based on established academic research in the field of **Mining Software Repositories (MSR)**:
- **Change Coupling**: Based on research on temporal dependencies (Gall et al., 1998) - [https://ieeexplore.ieee.org/document/738508](https://ieeexplore.ieee.org/document/738508).
- **Code Churn**: Standard metrics for measuring software evolution.
- **Forensic Repository Analysis**: Standard practices for identifying hotspots and architectural drift.

This project is an independent implementation focused on a novel domain: the synergy between human developers and agentic AI systems.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](https://github.com/brutus333/ai_collab_analyzer/blob/main/LICENSE) file for details.