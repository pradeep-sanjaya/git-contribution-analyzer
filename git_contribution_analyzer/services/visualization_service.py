"""Service for generating Git contribution visualizations."""
import logging
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

from ..config.config import VisualizationConfig
from ..config.output import REPORT_PATHS

class VisualizationService:
    """Service for generating visualizations of Git contributions."""

    def __init__(self, config: VisualizationConfig):
        """Initialize the visualization service."""
        self.config = config
        self.logger = logging.getLogger(__name__)

    def _format_date(self, date):
        """Format date for filenames."""
        return date.strftime('%Y%m%d')

    def generate_visualizations(self, stats_df: pd.DataFrame, output_dir: Path) -> None:
        """Generate visualizations from the statistics DataFrame."""
        if stats_df.empty:
            self.logger.warning("No data available for visualization")
            return

        # Create a date range for all months
        start_date = stats_df['date'].min()
        end_date = stats_df['date'].max()
        date_range = pd.date_range(start=start_date, end=end_date, freq='ME')

        # Create monthly contribution graph with all months
        monthly_commits = stats_df.groupby([
            pd.Grouper(key='date', freq='ME'),
            'author'
        ])['hash'].count().reset_index()

        # Get top contributors for better visualization
        top_authors = stats_df.groupby('author')['hash'].count().nlargest(self.config.top_n_contributors).index

        # Create the visualization
        plt.figure(figsize=(self.config.graph_width, self.config.graph_height))
        
        # Plot each author's contributions
        for author in top_authors:
            author_data = monthly_commits[monthly_commits['author'] == author]
            
            # Create a DataFrame with all months
            full_date_df = pd.DataFrame({'date': date_range})
            author_data = pd.merge(full_date_df, author_data, on='date', how='left')
            author_data['hash'] = author_data['hash'].fillna(0)
            
            plt.plot(author_data['date'], author_data['hash'], 
                    marker='o', label=author, linewidth=2, markersize=6)

        # Customize the plot
        plt.title('Monthly Contribution Activity by Top Contributors', 
                 fontsize=14, pad=20)
        plt.xlabel('Month', fontsize=12)
        plt.ylabel('Number of Commits', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Format x-axis to show all months
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        plt.xticks(rotation=45, ha='right')
        
        # Add legend
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', 
                  borderaxespad=0., fontsize=10)
        
        # Adjust layout to prevent label cutoff
        plt.tight_layout()

        # Save the graph
        start_date = self._format_date(stats_df['date'].min())
        end_date = self._format_date(stats_df['date'].max())
        output_path = output_dir / REPORT_PATHS['contribution_graph'].name.format(
            start_date=start_date,
            end_date=end_date
        )
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        self.logger.info(f"Generated contribution graph: {output_path}")
