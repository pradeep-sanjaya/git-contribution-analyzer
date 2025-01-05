# Git Contribution Report Generator

A Python-based tool for analyzing and visualizing Git repository contributions across multiple projects. This tool generates detailed reports and visualizations of commit activity, helping teams track and understand contribution patterns.

## Features

- **Multi-Repository Analysis**: Analyze multiple Git repositories simultaneously
- **Contribution Tracking**: Track commits, lines added/removed by author
- **Author Aliasing**: Consolidate different author names/emails under a single identity
- **Flexible Date Ranges**: Analyze contributions within specific time periods
- **Rich Visualizations**: Generate clear, informative graphs of contribution patterns
- **Detailed Reports**: Create comprehensive CSV reports including:
  - Daily activity breakdown
  - Author summaries
  - Repository summaries
  - Detailed commit logs

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd git_contribution_report
```

2. Install dependencies:
```bash
pip install pandas matplotlib
```

## Configuration

The tool uses configuration files in the `git_contribution_analyzer/config` directory:

### 1. Repository Configuration (`repositories.py`)
```python
REPOSITORIES = [
    'path/to/repository1',
    'path/to/repository2'
]
```

### 2. Author Configuration (`authors.py`)
```python
AUTHOR_ALIASES = {
    'email1@example.com': 'Preferred Name',
    'nickname': 'Preferred Name'
}

EXCLUDED_AUTHORS = {
    'bot@example.com',
    'system-user'
}
```

### 3. Date Configuration (`dates.py`)
```python
from datetime import datetime

START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2025, 1, 5)
```

## Usage

1. Configure the repositories and authors in their respective configuration files.
2. Run the analyzer:
```bash
python git_contribution_report.py
```

3. Find the generated reports in the `reports` directory:
- `git_commits_author_summary_YYYYMMDD_YYYYMMDD.csv`: Summary of contributions by author
- `git_commits_repository_summary_YYYYMMDD_YYYYMMDD.csv`: Summary of activity by repository
- `git_commits_daily_activity_YYYYMMDD_YYYYMMDD.csv`: Daily commit activity
- `git_commits_detailed_report_YYYYMMDD_YYYYMMDD.csv`: Detailed commit information
- `git_commits_contribution_graph_YYYYMMDD_YYYYMMDD.png`: Visual representation of contribution patterns

## Report Types

### 1. Author Summary
- Total commits per author
- Lines added/removed
- Active days
- First and last commit dates

### 2. Repository Summary
- Total commits per repository
- Number of contributors
- Active days
- First and last commit dates

### 3. Daily Activity
- Commits per day
- Active authors
- Lines changed
- Affected files

### 4. Detailed Report
- Complete commit history
- Hash, author, date
- Commit message
- Changed files
- Lines added/removed

### 5. Contribution Graph
- Visual timeline of commits
- Color-coded by author
- Monthly aggregation
- Interactive legend

## Customization

The tool can be customized by modifying:
- Visualization settings in `visualization_service.py`
- Output formats in `output.py`
- Analysis parameters in `analyzer.py`

## Tips

1. **Author Aliases**: Keep the `AUTHOR_ALIASES` dictionary updated to ensure accurate contribution tracking
2. **Date Ranges**: Adjust dates in `dates.py` for specific time periods
3. **Repository Paths**: Use relative paths from your workspace root in `repositories.py`
4. **Large Repositories**: For very large repositories, consider analyzing specific date ranges
5. **Output Location**: Reports are generated in the `reports` directory by default

## Troubleshooting

1. **No Data in Reports**
   - Check repository paths in `repositories.py`
   - Verify date range in `dates.py`
   - Ensure Git repositories are accessible

2. **Missing Authors**
   - Update `AUTHOR_ALIASES` with any new email/name combinations
   - Check `EXCLUDED_AUTHORS` for accidentally excluded contributors

3. **Performance Issues**
   - Reduce the date range
   - Limit the number of repositories
   - Update Git repositories before analysis
