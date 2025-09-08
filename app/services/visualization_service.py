"""Visualization service for data processing - handles BigQuery execution"""
import sys
import os
import pandas as pd
from typing import Optional, Protocol
from dataclasses import dataclass

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

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
