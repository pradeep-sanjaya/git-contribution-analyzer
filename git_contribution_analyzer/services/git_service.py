import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import pandas as pd

from ..config.config import GitConfig

class GitService:
    def __init__(self, config: GitConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def is_git_repository(self, path: Path) -> bool:
        """Check if a directory is a Git repository."""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--is-inside-work-tree'],
                cwd=str(path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return result.returncode == 0
        except Exception as e:
            self.logger.debug(f"Error checking if {path} is a git repository: {str(e)}")
            return False

    def get_repository_stats(self, repo_path: Path) -> pd.DataFrame:
        """Get Git statistics for a repository."""
        try:
            # Get list of commits
            git_log_cmd = [
                'git', 'log',
                f'--since={self.config.start_date.strftime("%Y-%m-%d")}',
                f'--until={self.config.end_date.strftime("%Y-%m-%d")}',
                '--format=%H|%ad|%an',
                '--date=format:%Y-%m-%d'
            ]
            
            result = subprocess.run(
                git_log_cmd,
                cwd=str(repo_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            if result.returncode != 0:
                self.logger.error(f"Error getting git log for {repo_path}: {result.stderr}")
                return pd.DataFrame()

            commits = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                    
                try:
                    commit_hash, date_str, author = line.strip().split('|')
                    author = author.lower()
                    
                    # Skip excluded authors
                    if author in self.config.excluded_authors:
                        continue
                        
                    # Apply author aliases
                    author = self.config.author_aliases.get(author, author)
                    
                    # Get commit stats
                    stats = self._get_commit_stats(commit_hash, repo_path)
                    if stats:
                        commits.append({
                            'date': datetime.strptime(date_str, '%Y-%m-%d'),
                            'author': author,
                            'hash': commit_hash,
                            'additions': stats['additions'],
                            'deletions': stats['deletions'],
                            'repository': repo_path.name
                        })
                except Exception as e:
                    self.logger.error(f"Error parsing commit line: {str(e)}")
                    continue

            if not commits:
                self.logger.info(f"No commits found in {repo_path.name}")
                return pd.DataFrame()

            return pd.DataFrame(commits)

        except Exception as e:
            self.logger.error(f"Error getting stats for {repo_path}: {str(e)}")
            return pd.DataFrame()

    def _get_commit_stats(self, commit_hash: str, repo_path: Path) -> Optional[dict]:
        """Get the number of additions and deletions for a commit."""
        try:
            result = subprocess.run(
                ['git', 'show', '--numstat', '--format=', commit_hash],
                cwd=str(repo_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            if result.returncode != 0:
                self.logger.error(f"Error getting commit stats: {result.stderr}")
                return None

            additions = 0
            deletions = 0
            
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                    
                try:
                    added, deleted, _ = line.split('\t')
                    if added != '-' and deleted != '-':  # Skip binary files
                        additions += int(added)
                        deletions += int(deleted)
                except ValueError:
                    continue

            return {
                'additions': additions,
                'deletions': deletions
            }

        except Exception as e:
            self.logger.error(f"Error getting commit stats: {str(e)}")
            return None
