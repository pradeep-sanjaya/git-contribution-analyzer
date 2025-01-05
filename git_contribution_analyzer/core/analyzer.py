import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import pandas as pd

from ..config.config import GitConfig, RepositoryConfig, VisualizationConfig
from ..services.git_service import GitService
from ..services.report_service import ReportService
from ..services.visualization_service import VisualizationService

class GitContributionAnalyzer:
    def __init__(
        self,
        git_config: GitConfig,
        repo_config: RepositoryConfig,
        viz_config: VisualizationConfig
    ):
        self.git_config = git_config
        self.repo_config = repo_config
        self.viz_config = viz_config
        
        self.git_service = GitService(git_config)
        self.report_service = ReportService()
        self.viz_service = VisualizationService(viz_config)
        
        self.logger = logging.getLogger(__name__)

    def analyze(self) -> None:
        """Run the complete analysis process."""
        self.logger.info("\nAnalyzing repositories for commits between %s and %s...\n", 
                        self.git_config.start_date.strftime("%Y-%m-%d"),
                        self.git_config.end_date.strftime("%Y-%m-%d"))

        # Find repositories
        repositories = self._find_repositories()
        self.logger.info("Checking repositories:")
        for repo_path in repositories:
            status = "Valid Git Repository" if self.git_service.is_git_repository(repo_path) else "Not a Git Repository"
            self.logger.info(f"- {repo_path} ({status})")
        self.logger.info("")

        # Gather statistics
        self.logger.info("Gathering statistics...\n")
        stats_data = []
        for i, repo_path in enumerate(repositories, 1):
            repo_name = repo_path.name
            self.logger.info(f"Processing repository {i}/{len(repositories)}: {repo_name}")
            
            try:
                if not self.git_service.is_git_repository(repo_path):
                    self.logger.info(f"Not a git repository: {repo_path}")
                    self.logger.info(f"No commits found in {repo_name}\n")
                    continue

                repo_stats = self.git_service.get_repository_stats(repo_path)
                if not repo_stats.empty:
                    stats_data.append(repo_stats)
                    self.logger.info(f"Successfully analyzed {repo_name}\n")
                else:
                    self.logger.info(f"No commits found in {repo_name}\n")

            except Exception as e:
                self.logger.error(f"Error processing {repo_name}: {str(e)}\n")

        if not stats_data:
            self.logger.error("No data found in any repository.")
            return

        # Combine all stats
        combined_stats = pd.concat(stats_data, ignore_index=True)

        # Generate reports
        self.logger.info("Generating reports...\n")
        self.report_service.generate_reports(combined_stats, self.viz_config.output_dir)
        
        # Create visualization
        self.viz_service.generate_visualizations(combined_stats, self.viz_config.output_dir)

    def _find_repositories(self) -> List[Path]:
        """Find all Git repositories in the configured base paths."""
        repositories = []
        
        for base_path in self.repo_config.base_paths:
            self.logger.info(f"Searching in base path: {base_path}")
            if not base_path.exists():
                self.logger.warning(f"Base path does not exist: {base_path}")
                continue

            # Handle the base path itself if it's a Git repository
            if self.git_service.is_git_repository(base_path):
                repositories.append(base_path)
                self.logger.info(f"Found Git repository at base path: {base_path}")
                continue

            # Search for repositories in subdirectories
            for path in base_path.rglob('.git'):
                repo_path = path.parent
                
                # Check repository depth
                depth = len(repo_path.relative_to(base_path).parts)
                if depth < self.repo_config.min_repo_depth or depth > self.repo_config.max_repo_depth:
                    self.logger.debug(f"Skipping {repo_path} due to depth {depth}")
                    continue

                # Check if path is excluded
                if any(excl in str(repo_path) for excl in self.repo_config.excluded_paths):
                    self.logger.debug(f"Skipping excluded path: {repo_path}")
                    continue

                repositories.append(repo_path)
                self.logger.info(f"Found Git repository: {repo_path}")

        return sorted(repositories)
