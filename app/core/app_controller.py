from typing import Optional, Callable, Any
from dataclasses import dataclass

from core.models import SearchRequest, SearchResponse, ConnectionStatus, AppStats
from utils.connection_utils import check_bigquery_connection, validate_environment, get_app_stats, format_number
from utils.gcp_auth import get_bigquery_client
from services.semantic_search import SemanticSearchService, SearchConfig
from services.visualization_service import VisualizationService
import pandas as pd


@dataclass
class AppConfig:
    """Configuration for application controller"""
    project_id: str
    dataset_id: str = "patent_analysis"
    
    @classmethod
    def from_environment(cls) -> 'AppConfig':
        """Create config from settings (supports Streamlit secrets fallback)"""
        from config.settings import GOOGLE_CLOUD_PROJECT_ID, BQ_DATASET_ID
        project_id = GOOGLE_CLOUD_PROJECT_ID
        if not project_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT_ID environment variable is required")
        dataset_id = BQ_DATASET_ID or "patent_analysis"
        return cls(project_id=project_id, dataset_id=dataset_id)


class AppController:
    """Main application controller handling all business logic"""
    
    def __init__(self, 
                 config: Optional[AppConfig] = None,
                 bigquery_client=None, 
                 visualization_service=None, 
                 semantic_search_service=None,
                 bigquery_client_provider: Optional[Callable[[], Any]] = None):
        """
        Initialize the controller with configuration and optional dependencies for testing
        
        Args:
            config: Application configuration (if None, loads from environment)
            bigquery_client: Optional BigQuery client for testing
            visualization_service: Optional visualization service for testing  
            semantic_search_service: Optional search service for testing
        """
        self.config = config or AppConfig.from_environment()
        self._bigquery_client = bigquery_client
        self._visualization_service = visualization_service
        self._semantic_search_service = semantic_search_service
        # Provider function for obtaining a BigQuery client (DI-friendly)
        self._bigquery_client_provider = bigquery_client_provider or (lambda: get_bigquery_client())
    
    def _get_bigquery_setup(self):
        """Get BigQuery client and project ID, return (client, project_id, error_message)"""
        # Check connection first
        connection_status = self.get_connection_status()
        if not connection_status.gcp_connected:
            return None, None, f"BigQuery not connected: {connection_status.gcp_message}"
        
        # Get BigQuery client
        if not self._bigquery_client:
            # Use injected provider (defaults to standard get_bigquery_client)
            self._bigquery_client = self._bigquery_client_provider()
        
        if not self._bigquery_client:
            return None, None, "Failed to get BigQuery client"
        
        # Use project ID from config
        return self._bigquery_client, self.config.project_id, None
    
    def _get_visualization_service(self):
        """Get visualization service instance"""
        if not self._visualization_service:
            client, project_id, error = self._get_bigquery_setup()
            if error:
                return None
            self._visualization_service = VisualizationService(client)
        return self._visualization_service
    
    def _get_semantic_search_service(self):
        """Get semantic search service instance"""
        if not self._semantic_search_service:
            client, project_id, error = self._get_bigquery_setup()
            if error:
                return None
            config = SearchConfig(project_id=project_id, dataset_id=self.config.dataset_id)
            self._semantic_search_service = SemanticSearchService(config, client)
        return self._semantic_search_service
    
    def _format_search_results(self, df: pd.DataFrame) -> pd.DataFrame:
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
    
    def format_search_results_for_display(self, response: SearchResponse) -> pd.DataFrame:
        """Convert SearchResponse to display DataFrame - extracted from dashboard"""
        data = []
        for result in response.results:
            data.append({
                "Patent URI": result.patent_uri,
                "Component": result.component,
                "Function": result.function,
                "Similarity": result.similarity
            })
        
        return pd.DataFrame(data)
    
    def get_formatted_component_outliers(self):
        """Get component outliers with display formatting"""
        success, message, df_outliers = self.get_component_outliers()
        if success and df_outliers is not None and not df_outliers.empty:
            visualization_service = self._get_visualization_service()
            if visualization_service:
                formatted_df = visualization_service.format_outlier_data_for_display(df_outliers)
                return success, message, formatted_df
        return success, message, df_outliers
    
    def get_formatted_distribution_chart_data(self):
        """Get component distribution with chart formatting"""
        success, message, df_distribution = self.get_component_distribution()
        if success and df_distribution is not None:
            # Also get outliers for chart markers
            outlier_success, _, df_outliers = self.get_component_outliers()
            visualization_service = self._get_visualization_service()
            if visualization_service:
                chart_data = visualization_service.format_distribution_chart_data(
                    df_distribution, df_outliers if outlier_success else None
                )
                return success, message, chart_data
        return success, message, None
    
    def get_formatted_portfolio_chart_data(self):
        """Get portfolio analysis with chart formatting"""
        success, message, df_portfolio = self.get_portfolio_analysis()
        if success and df_portfolio is not None:
            visualization_service = self._get_visualization_service()
            if visualization_service:
                chart_data = visualization_service.format_portfolio_chart_data(df_portfolio)
                return success, message, chart_data
        return success, message, None
    
    def get_connection_status(self) -> ConnectionStatus:
        """Get current connection status"""
        env_valid, env_msg = validate_environment()
        # Use injected or cached client for the connectivity probe
        client = self._bigquery_client or self._bigquery_client_provider()
        gcp_connected, gcp_msg = check_bigquery_connection(client)
        
        return ConnectionStatus(
            env_valid=env_valid,
            env_message=env_msg,
            gcp_connected=gcp_connected,
            gcp_message=gcp_msg
        )
    
    def get_app_stats(self) -> Optional[AppStats]:
        """Get application statistics"""
        try:
            # Prefer existing/injected client for stats query to avoid re-auth
            client = self._bigquery_client or self._bigquery_client_provider()
            stats = get_app_stats(client)
            return AppStats(
                patent_count=format_number(stats["patent_count"]),
                component_count=format_number(stats["component_count"]),
                connection_status=stats.get('connection_status', 'Unknown')
            )
        except Exception:
            return None
    
    def search_patents(self, request: SearchRequest) -> SearchResponse:
        """Perform patent search"""
        # Get semantic search service
        semantic_search_service = self._get_semantic_search_service()
        if not semantic_search_service:
            return SearchResponse(success=False, message="Semantic search service not available", query=request.query)

        try:
            # Perform search using the service
            search_result = semantic_search_service.run_semantic_search(request.query)
            
            if search_result["success"]:
                results_df = search_result["results"]
                
                if not results_df.empty:
                    # Convert DataFrame to display format
                    display_df = self._format_search_results(results_df)
                    
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
    
    def get_component_outliers(self):
        """Get component outliers analysis"""
        visualization_service = self._get_visualization_service()
        if not visualization_service:
            return False, "Visualization service not available", None
        
        try:
            result = visualization_service.detect_component_outliers(self.config.project_id)
            return result.success, result.message, result.data
        except Exception as e:
            return False, f"Outlier analysis failed: {str(e)}", None
    
    def get_component_distribution(self):
        """Get component distribution data for histogram"""
        visualization_service = self._get_visualization_service()
        if not visualization_service:
            return False, "Visualization service not available", None
        
        try:
            result = visualization_service.get_component_distribution_data(self.config.project_id)
            return result.success, result.message, result.data
        except Exception as e:
            return False, f"Distribution analysis failed: {str(e)}", None
    
    def get_portfolio_analysis(self):
        """Get portfolio analysis data for bubble chart"""
        visualization_service = self._get_visualization_service()
        if not visualization_service:
            return False, "Visualization service not available", None
        
        try:
            result = visualization_service.get_portfolio_analysis_data(self.config.project_id)
            return result.success, result.message, result.data
        except Exception as e:
            return False, f"Portfolio analysis failed: {str(e)}", None
