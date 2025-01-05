from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Set, Dict

@dataclass
class GitConfig:
    start_date: datetime
    end_date: datetime
    author_aliases: dict = field(default_factory=dict)
    excluded_authors: set = field(default_factory=set)

@dataclass
class RepositoryConfig:
    base_paths: List[Path]
    excluded_paths: set = field(default_factory=set)
    min_repo_depth: int = 3
    max_repo_depth: int = 5

@dataclass
class VisualizationConfig:
    top_n_contributors: int = 20
    top_n_repos: int = 20
    graph_width: int = 15
    graph_height: int = 8
    graph_title: str = "Monthly Contribution Activity"
    output_dir: Path = Path("reports")
