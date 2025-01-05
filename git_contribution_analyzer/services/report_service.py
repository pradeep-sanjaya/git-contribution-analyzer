"""Service for generating Git contribution reports."""
import logging
from pathlib import Path
import pandas as pd
from ..config.output import REPORT_PATHS

class ReportService:
    """Service for generating Git contribution reports."""

    def __init__(self):
        """Initialize the report service."""
        self.logger = logging.getLogger(__name__)

    def _format_date(self, date):
        """Format date for filenames."""
        return date.strftime('%Y%m%d')

    def generate_reports(self, df: pd.DataFrame, output_dir: Path):
        """Generate all reports from the statistics DataFrame."""
        if df.empty:
            self.logger.warning("No data available to generate reports")
            return

        # Get date range for filenames
        start_date = self._format_date(df['date'].min())
        end_date = self._format_date(df['date'].max())

        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate author summary
        author_summary = self._generate_author_summary(df)
        author_summary.to_csv(
            output_dir / REPORT_PATHS['author_summary'].name.format(
                start_date=start_date, end_date=end_date
            )
        )

        # Generate daily activity
        daily_activity = self._generate_daily_activity(df)
        daily_activity.to_csv(
            output_dir / REPORT_PATHS['daily_activity'].name.format(
                start_date=start_date, end_date=end_date
            )
        )

        # Generate repository summary
        repo_summary = self._generate_repository_summary(df)
        repo_summary.to_csv(
            output_dir / REPORT_PATHS['repository_summary'].name.format(
                start_date=start_date, end_date=end_date
            )
        )

        # Generate detailed report
        self._generate_detailed_report(
            df, author_summary, daily_activity, repo_summary,
            output_dir / REPORT_PATHS['detailed_report'].name.format(
                start_date=start_date, end_date=end_date
            )
        )

    def _generate_author_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate author summary report."""
        summary = df.groupby('author').agg({
            'hash': 'count',
            'additions': 'sum',
            'deletions': 'sum'
        }).rename(columns={'hash': 'commits'})
        
        summary['total_lines'] = summary['additions'] + summary['deletions']
        summary = summary.sort_values('commits', ascending=False)
        
        return summary

    def _generate_daily_activity(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate daily activity report."""
        daily = df.groupby(['date', 'author']).agg({
            'hash': 'count',
            'additions': 'sum',
            'deletions': 'sum'
        }).rename(columns={'hash': 'commits'})
        
        # Sort by date and commits within each date
        daily = daily.reset_index().sort_values(['date', 'commits'], ascending=[True, False])
        daily = daily.set_index(['date', 'author'])
        
        return daily

    def _generate_repository_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate repository summary report."""
        repo_summary = df.groupby(['repository', 'author']).agg({
            'hash': 'count',
            'additions': 'sum',
            'deletions': 'sum'
        }).rename(columns={'hash': 'commits'})
        
        # Sort repositories by total commits and authors within repositories by commits
        repo_summary = repo_summary.reset_index()
        repo_totals = repo_summary.groupby('repository')['commits'].sum()
        repo_summary['repo_total_commits'] = repo_summary['repository'].map(repo_totals)
        repo_summary = repo_summary.sort_values(['repo_total_commits', 'commits'], ascending=[False, False])
        repo_summary = repo_summary.drop('repo_total_commits', axis=1)
        repo_summary = repo_summary.set_index(['repository', 'author'])
        
        return repo_summary

    def _generate_detailed_report(self, df: pd.DataFrame, author_summary: pd.DataFrame,
                                daily_activity: pd.DataFrame, repo_summary: pd.DataFrame,
                                output_file: Path):
        """Generate a detailed text report combining all statistics."""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("DETAILED CONTRIBUTION REPORT\n")
            f.write("=" * 80 + "\n\n")

            # Top 10 Contributors
            f.write("1. TOP 10 CONTRIBUTORS BY TOTAL IMPACT\n")
            f.write("-" * 50 + "\n\n")
            for author in author_summary.head(10).index:
                stats = author_summary.loc[author]
                f.write(f"{author}:\n")
                f.write(f"  Commits: {stats['commits']:,}\n")
                f.write(f"  Lines Added: {stats['additions']:,}\n")
                f.write(f"  Lines Deleted: {stats['deletions']:,}\n")
                f.write(f"  Total Lines Modified: {stats['total_lines']:,}\n\n")

            # Monthly Activity
            f.write("2. MONTHLY ACTIVITY\n")
            f.write("-" * 50 + "\n\n")
            monthly = df.groupby([df['date'].dt.strftime('%Y-%m')]).agg({
                'hash': 'count'
            }).rename(columns={'hash': 'commits'})

            for month in monthly.index:
                f.write(f"{month}:\n")
                f.write(f"  Total Commits: {monthly.loc[month, 'commits']}\n")
                
                # Top contributors for the month
                month_contributors = df[df['date'].dt.strftime('%Y-%m') == month].groupby('author')['hash'].count()
                f.write("  Top Contributors:\n")
                for author, commits in month_contributors.sort_values(ascending=False).head(3).items():
                    f.write(f"    - {author}: {commits} commits\n")
                f.write("\n")

            # Repository Activity
            f.write("3. REPOSITORY ACTIVITY\n")
            f.write("-" * 50 + "\n\n")
            repo_totals = df.groupby('repository')['hash'].count().sort_values(ascending=False)
            
            for repo in repo_totals.index:
                f.write(f"{repo}:\n")
                f.write(f"  Total Commits: {repo_totals[repo]}\n")
                
                # Top contributors for the repository
                repo_contributors = df[df['repository'] == repo].groupby('author')['hash'].count()
                f.write("  Top Contributors:\n")
                for author, commits in repo_contributors.sort_values(ascending=False).head(2).items():
                    f.write(f"    - {author}: {commits} commits\n")
                f.write("\n")
