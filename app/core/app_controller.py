"""Main application controller - business logic and coordination"""
import sys
import os
from typing import Optional

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.models import SearchRequest, SearchResponse, ConnectionStatus, AppStats
from utils.data_processor import test_gcp_connection, validate_environment, get_app_stats, format_number
from utils.gcp_auth import get_bigquery_client
from utils.semantic_search import run_semantic_search
from services.visualization_service import detect_component_outliers, get_component_distribution_data, get_portfolio_analysis_data
import pandas as pd


class AppController:
    """Main application controller handling all business logic"""
    
    def __init__(self):
        """Initialize the controller"""
        self._bigquery_client = None
    
    def get_connection_status(self) -> ConnectionStatus:
        """Get current connection status"""
        env_valid, env_msg = validate_environment()
        gcp_connected, gcp_msg = test_gcp_connection()
        
        return ConnectionStatus(
            env_valid=env_valid,
            env_message=env_msg,
            gcp_connected=gcp_connected,
            gcp_message=gcp_msg
        )
    
    def get_app_stats(self) -> Optional[AppStats]:
        """Get application statistics"""
        try:
            stats = get_app_stats()
            return AppStats(
                patent_count=format_number(stats["patent_count"]),
                component_count=format_number(stats["component_count"]),
                connection_status=stats.get('connection_status', 'Unknown')
            )
        except Exception:
            return None
    
    def search_patents(self, request: SearchRequest) -> SearchResponse:
        """Perform patent search"""
        # Validate connection first
        connection_status = self.get_connection_status()
        
        if not connection_status.gcp_connected:
            return SearchResponse(
                success=False,
                message=f"BigQuery not connected: {connection_status.gcp_message}",
                query=request.query
            )
        
        try:
            # Get BigQuery client
            if not self._bigquery_client:
                self._bigquery_client = get_bigquery_client()
            
            if not self._bigquery_client:
                return SearchResponse(
                    success=False,
                    message="Failed to get BigQuery client",
                    query=request.query
                )
            
            # Perform search
            search_result = run_semantic_search(request.query, self._bigquery_client)
            
            if search_result["success"]:
                results_df = search_result["results"]
                
                if not results_df.empty:
                    # Convert DataFrame to display format
                    display_df = self._prepare_results_dataframe(results_df)
                    
                    return SearchResponse.from_dataframe(
                        success=True,
                        message=search_result["message"],
                        df=display_df,
                        query=request.query
                    )
                else:
                    return SearchResponse(
                        success=True,
                        message=search_result["message"],
                        query=request.query
                    )
            else:
                return SearchResponse(
                    success=False,
                    message=search_result["message"],
                    query=request.query
                )
                
        except Exception as e:
            return SearchResponse(
                success=False,
                message=f"Search failed: {str(e)}",
                query=request.query
            )
    
    def _prepare_results_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert search results DataFrame to display format"""
        display_df = df.copy()
        
        # Rename columns for better display
        display_df = display_df.rename(columns={
            'uri': 'Patent URI',
            'component_name': 'Component',
            'component_function': 'Function',
        })
        
        # Calculate similarity percentage
        display_df['Similarity'] = ((1 - display_df['distance']) * 100).round().astype(int)
        
        # Drop the distance column
        display_df = display_df.drop(columns=['distance'])
        
        # Reorder columns
        columns_order = ['Patent URI', 'Component', 'Function', 'Similarity']
        display_df = display_df[columns_order]
        
        return display_df
    
    def get_component_outliers(self):
        """Get component outliers analysis"""
        # Check connection
        connection_status = self.get_connection_status()
        if not connection_status.gcp_connected:
            return False, f"BigQuery not connected: {connection_status.gcp_message}", None
        
        try:
            # Get BigQuery client
            if not self._bigquery_client:
                self._bigquery_client = get_bigquery_client()
            
            if not self._bigquery_client:
                return False, "Failed to get BigQuery client", None
            
            # Get project ID from environment
            import os
            project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
            if not project_id:
                return False, "GOOGLE_CLOUD_PROJECT_ID not configured", None
            
            return detect_component_outliers(self._bigquery_client, project_id)
            
        except Exception as e:
            return False, f"Outlier analysis failed: {str(e)}", None
    
    def get_component_distribution(self):
        """Get component distribution data for histogram"""
        # Check connection
        connection_status = self.get_connection_status()
        if not connection_status.gcp_connected:
            return False, f"BigQuery not connected: {connection_status.gcp_message}", None
        
        try:
            # Get BigQuery client
            if not self._bigquery_client:
                self._bigquery_client = get_bigquery_client()
            
            if not self._bigquery_client:
                return False, "Failed to get BigQuery client", None
            
            # Get project ID from environment
            import os
            project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
            if not project_id:
                return False, "GOOGLE_CLOUD_PROJECT_ID not configured", None
            
            return get_component_distribution_data(self._bigquery_client, project_id)
            
        except Exception as e:
            return False, f"Distribution analysis failed: {str(e)}", None
    
    def get_portfolio_analysis(self):
        """Get portfolio analysis data for bubble chart"""
        # Check connection
        connection_status = self.get_connection_status()
        if not connection_status.gcp_connected:
            return False, f"BigQuery not connected: {connection_status.gcp_message}", None
        
        try:
            # Get BigQuery client
            if not self._bigquery_client:
                self._bigquery_client = get_bigquery_client()
            
            if not self._bigquery_client:
                return False, "Failed to get BigQuery client", None
            
            # Get project ID from environment
            import os
            project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
            if not project_id:
                return False, "GOOGLE_CLOUD_PROJECT_ID not configured", None
            
            return get_portfolio_analysis_data(self._bigquery_client, project_id)
            
        except Exception as e:
            return False, f"Portfolio analysis failed: {str(e)}", None
