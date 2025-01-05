"""Git contribution analyzer main script."""

import logging
from pathlib import Path

from git_contribution_analyzer.config.config import GitConfig, RepositoryConfig, VisualizationConfig
from git_contribution_analyzer.config.authors import AUTHOR_ALIASES, EXCLUDED_AUTHORS
from git_contribution_analyzer.config.repositories import REPOSITORIES
from git_contribution_analyzer.config.dates import START_DATE, END_DATE
from git_contribution_analyzer.config.output import DEFAULT_OUTPUT_DIR
from git_contribution_analyzer.core.analyzer import GitContributionAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(message)s')

def main():
    """Run the Git contribution analyzer."""
    # Get script directory
    script_dir = Path(__file__).resolve().parent
    
    # Initialize configurations
    repo_config = RepositoryConfig(
        base_paths=[script_dir.parent / repo for repo in REPOSITORIES],
        excluded_paths=set(),
        min_repo_depth=0,
        max_repo_depth=1
    )

    git_config = GitConfig(
        start_date=START_DATE,
        end_date=END_DATE,
        author_aliases=AUTHOR_ALIASES,
        excluded_authors=EXCLUDED_AUTHORS
    )

    viz_config = VisualizationConfig(output_dir=DEFAULT_OUTPUT_DIR)

    # Create and run analyzer
    analyzer = GitContributionAnalyzer(
        repo_config=repo_config,
        git_config=git_config,
        viz_config=viz_config
    )
    analyzer.analyze()


if __name__ == '__main__':
    main()
