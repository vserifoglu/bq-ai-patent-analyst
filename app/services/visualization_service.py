"""Visualization service for data processing - handles BigQuery execution"""
import pandas as pd
from typing import Optional, Protocol
from dataclasses import dataclass

from utils.visualization_queries import (
    get_outlier_detection_query,
    get_component_distribution_query,
    get_portfolio_analysis_query
)


class BigQueryClient(Protocol):
    """Protocol for BigQuery client to enable dependency injection"""
    def query(self, sql: str) -> 'QueryResult':
        ...


class QueryResult(Protocol):
    """Protocol for query result to enable mocking"""
    def to_dataframe(self) -> pd.DataFrame:
        ...


@dataclass
class VisualizationResult:
    """Structured result for visualization operations"""
    success: bool
    message: str
    data: Optional[pd.DataFrame] = None
    error_type: Optional[str] = None


class VisualizationService:
    """Service for visualization data processing with dependency injection"""
    
    def __init__(self, bigquery_client: Optional[BigQueryClient] = None):
        """Initialize with optional BigQuery client for testing"""
        self.client = bigquery_client
    
    def _execute_query(self, query: str, operation_name: str) -> VisualizationResult:
        """Execute BigQuery query with consistent error handling"""
        if not self.client:
            return VisualizationResult(
                success=False,
                message="BigQuery client not available",
                error_type="client_unavailable"
            )
        
        try:
            result = self.client.query(query)
            df = result.to_dataframe()
            
            if df.empty:
                return VisualizationResult(
                    success=True,
                    message=f"No data found for {operation_name}",
                    data=df
                )
            
            return VisualizationResult(
                success=True,
                message=f"Retrieved {operation_name} data for {len(df)} records",
                data=df
            )
            
        except Exception as e:
            return VisualizationResult(
                success=False,
                message=f"{operation_name} failed: {str(e)}",
                error_type="query_execution_error"
            )

    def detect_component_outliers(self, project_id: str) -> VisualizationResult:
        """
        Detect patents with anomalous number of components
        """
        query = get_outlier_detection_query(project_id)
        result = self._execute_query(query, "outlier detection")
        
        # Custom message for outlier detection
        if result.success and result.data is not None:
            if result.data.empty:
                result.message = "No significant outliers found in component counts."
            else:
                result.message = f"Found {len(result.data)} patents with unusually high number of components."
        
        return result
    
    def get_component_distribution_data(self, project_id: str) -> VisualizationResult:
        """
        Get component count distribution data for histogram
        """
        query = get_component_distribution_query(project_id)
        result = self._execute_query(query, "component distribution")
        
        # Custom message for distribution
        if result.success and result.data is not None and not result.data.empty:
            result.message = f"Retrieved component distribution for {len(result.data)} patents."
        
        return result
    
    def get_portfolio_analysis_data(self, project_id: str) -> VisualizationResult:
        """
        Get strategic patent portfolio analysis data for bubble chart
        """
        query = get_portfolio_analysis_query(project_id)
        result = self._execute_query(query, "portfolio analysis")
        
        # Custom message for portfolio analysis
        if result.success and result.data is not None and not result.data.empty:
            result.message = f"Retrieved portfolio analysis for {len(result.data)} applicants."
        
        return result
    
    def format_outlier_data_for_display(self, df_outliers: pd.DataFrame) -> pd.DataFrame:
        """Format outlier data for UI display table"""
        if df_outliers is None or df_outliers.empty:
            return df_outliers
            
        display_df = df_outliers.copy()
        # Extract patent ID from URI
        display_df['Patent'] = display_df['uri'].apply(lambda x: x.split('/')[-1])
        # Select and rename columns
        display_df = display_df[['Patent', 'num_components']].rename(columns={
            'Patent': 'Patent ID',
            'num_components': 'Component Count'
        })
        # Sort by component count (descending)
        display_df = display_df.sort_values('Component Count', ascending=False)
        
        return display_df
    
    def format_distribution_chart_data(self, df_distribution: pd.DataFrame, df_outliers: Optional[pd.DataFrame] = None) -> dict:
        """Format distribution data for histogram chart with complete figure"""
        try:
            import plotly.express as px
            
            # Create histogram with descriptive title
            fig = px.histogram(
                df_distribution,
                x="num_components",
                title="",
                labels={"num_components": "Number of Components per Patent"}
            )
            
            # Add outlier markers if available
            if df_outliers is not None and not df_outliers.empty:
                for _, row in df_outliers.iterrows():
                    fig.add_vline(
                        x=row['num_components'],
                        line_width=2,
                        line_dash="dash",
                        line_color="red"
                    )
            
            # Add an annotation for outliers (long tail)
            try:
                x_max = float(df_distribution["num_components"].max())
            except Exception:
                x_max = None
            fig.add_annotation(
                x=x_max if x_max is not None else 0,
                xref="x",
                y=1.02,
                yref="paper",
                showarrow=False,
                text="Outliers: Highly Complex Inventions (>3 std. dev.)",
                align="right"
            )

            # Configure layout and center title
            fig.update_layout(
                xaxis_title="Number of Components",
                yaxis_title="Number of Patents",
                font=dict(family="Arial, sans-serif", size=12),
                height=400
            )
            
            return {
                'figure': fig,
                'has_plotly': True
            }
            
        except ImportError:
            return {
                'figure': None,
                'has_plotly': False,
                'error': "Plotly not available"
            }
    
    def format_portfolio_chart_data(self, df_portfolio: pd.DataFrame) -> dict:
        """Format portfolio data for bubble chart with complete figure"""
        try:
            import plotly.express as px
            
            # Create bubble chart
            fig = px.scatter(
                df_portfolio,
                x="innovation_breadth",
                y="average_connection_density",
                size="total_patents",
                color="applican",
                hover_name="applican",
                size_max=60,
                title="",
                labels={
                    "innovation_breadth": "Innovation Breadth (Number of Unique Domains)",
                    "average_connection_density": "Architectural Complexity (Avg. Connections per Patent)"
                }
            )
            
            # Configure layout
            fig.update_layout(
                showlegend=False,
                xaxis_title="Innovation Breadth (Number of Unique Domains)",
                yaxis_title="Architectural Complexity (Avg. Connections per Patent)",
                height=400
            )
            
            return {
                'figure': fig,
                'has_plotly': True
            }
            
        except ImportError:
            return {
                'figure': None,
                'has_plotly': False,
                'error': "Plotly not available"
            }
