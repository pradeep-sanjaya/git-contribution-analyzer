"""Output configuration for Git contribution analyzer."""
from pathlib import Path

# Report output paths
REPORT_PATHS = {
    'author_summary': Path('git_commits_author_summary_{start_date}_{end_date}.csv'),
    'daily_activity': Path('git_commits_daily_activity_{start_date}_{end_date}.csv'),
    'repository_summary': Path('git_commits_repository_summary_{start_date}_{end_date}.csv'),
    'contribution_graph': Path('git_commits_contribution_graph_{start_date}_{end_date}.png'),
    'detailed_report': Path('git_commits_detailed_report_{start_date}_{end_date}.csv')
}

# Default output directory
DEFAULT_OUTPUT_DIR = Path('reports')
