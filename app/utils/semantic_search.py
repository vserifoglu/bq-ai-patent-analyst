"""
Semantic Search Module for Patent Analysis
Simple implementation with independent, testable functions.
"""

from google.cloud import bigquery
from typing import Optional, Dict, Any, Tuple
import pandas as pd
from dataclasses import dataclass


@dataclass
class SearchConfig:
    """Configuration for semantic search operations"""
    project_id: str
    dataset_id: str = "patent_analysis"
    embedding_model: str = "embedding_model"
    classification_model: str = "gemini_vision_analyzer"
    search_index: str = "component_search_index"


class SemanticSearchService:
    """Service class for semantic search operations with dependency injection"""
    
    def __init__(self, config: SearchConfig, bigquery_client: Optional[bigquery.Client] = None):
        """Initialize with configuration and optional BigQuery client for testing"""
        self.config = config
        self.client = bigquery_client
    
    def sanitize_for_sql(self, query: str) -> str:
        """
        Basic sanitization for SQL safety.
        
        Args:
            query: Raw user input
            
        Returns:
            Sanitized query string
        """
        if not isinstance(query, str):
            return ""
        
        return query.replace("'", "\\'")
    
    def _build_classification_query(self, search_query: str) -> str:
        """Build SQL query for technical classification - extracted for testing"""
        classification_prompt = f"""
            Is the following user query related to a technical, scientific, 
            or engineering topic? Answer with only 'Yes' or 'No'. Query: {search_query}
        """
        
        return f"""
        SELECT ml_generate_text_llm_result
        FROM ML.GENERATE_TEXT(
            MODEL `{self.config.project_id}.{self.config.dataset_id}.{self.config.classification_model}`,
            (SELECT '''{classification_prompt}''' AS prompt),
            STRUCT(
                0.0 AS temperature, 
                TRUE AS flatten_json_output, 
                1024 AS max_output_tokens
            )
        )
        """
    def is_query_technical(self, search_query: str) -> Tuple[bool, Optional[str]]:
        """
        Classify whether a query is technical using BigQuery ML.
        
        Args:
            search_query: The user's search query (should be sanitized externally)
            
        Returns:
            Tuple of (is_technical: bool, error_message: Optional[str])
        """
        if not self.client:
            return False, "BigQuery client not available"
            
        sql_query = self._build_classification_query(search_query)
        
        try:
            query_job = self.client.query(sql_query)
            results = query_job.result()
            for row in results:
                response = row.ml_generate_text_llm_result.strip().lower()
                if "yes" in response:
                    return True, None
            return False, None
        except Exception as e:
            return False, f"Error during query classification: {str(e)}"
    
    def _build_vector_search_query(self, search_query: str, distance_threshold: float, top_k: int) -> str:
        """Build SQL query for vector search - extracted for testing"""
        return f"""
            WITH search_results AS (
              SELECT
                base.uri, base.component_name, base.component_function, distance
              FROM
                VECTOR_SEARCH(
                  TABLE `{self.config.project_id}.{self.config.dataset_id}.{self.config.search_index}`,
                  'combined_vector',
                  (
                    SELECT ml_generate_embedding_result
                    FROM ML.GENERATE_EMBEDDING(
                      MODEL `{self.config.project_id}.{self.config.dataset_id}.{self.config.embedding_model}`,
                      (
                        SELECT CONCAT('Represent this technical patent component for semantic search: ', '{search_query}') AS content
                      )
                    )
                  ),
                  top_k => {top_k},
                  distance_type => 'COSINE'
                )
            )
            SELECT * FROM search_results WHERE distance < {distance_threshold};
        """

    def perform_vector_search(
        self, 
        search_query: str, 
        distance_threshold: float = 0.8,
        top_k: int = 70
    ) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
        """
        Perform vector search on patent components.
        
        Args:
            search_query: Sanitized search query
            distance_threshold: Maximum cosine distance for results
            top_k: Number of top results to fetch
            
        Returns:
            Tuple of (DataFrame with search results or None, error_message)
        """
        if not self.client:
            return None, "BigQuery client not available"
            
        sql_query = self._build_vector_search_query(search_query, distance_threshold, top_k)
        
        try:
            df = self.client.query(sql_query).to_dataframe()
            return df, None
        except Exception as e:
            return None, f"Vector search failed: {str(e)}"
    
    def run_semantic_search(
        self, 
        raw_query: str, 
        distance_threshold: float = 0.8,
        top_k: int = 70,
        skip_classification: bool = False
    ) -> Dict[str, Any]:
        """
        Main orchestrator function that combines all search steps.
        
        Args:
            raw_query: Raw user input
            distance_threshold: Maximum cosine distance for results
            top_k: Number of top results to fetch
            skip_classification: Skip technical classification (useful for testing)
            
        Returns:
            Dictionary with success status, message, and results
        """
        # Step 1: Sanitize input
        sanitized_query = self.sanitize_for_sql(raw_query)
        
        if not sanitized_query:
            return {
                "success": False,
                "message": "Please enter a valid search query.",
                "results": None
            }
        
        # Step 2: Check if query is technical (unless skipped)
        if not skip_classification:
            is_technical, error = self.is_query_technical(sanitized_query)
            if error:
                return {
                    "success": False,
                    "message": f"Classification failed: {error}",
                    "results": None
                }
            if not is_technical:
                return {
                    "success": False,
                    "message": "Query is not technical. Please enter a query related to a technical component or function.",
                    "results": None
                }
        
        # Step 3: Perform vector search
        results_df, error = self.perform_vector_search(
            sanitized_query, 
            distance_threshold=distance_threshold,
            top_k=top_k
        )
        
        if error:
            return {
                "success": False,
                "message": error,
                "results": None
            }
        
        if results_df is None or results_df.empty:
            return {
                "success": True,
                "message": f"No results found for '{raw_query}'. Try a different query.",
                "results": results_df or pd.DataFrame()
            }
        
        return {
            "success": True,
            "message": f"Found {len(results_df)} results for '{raw_query}'.",
            "results": results_df
        }


# Backward compatibility functions for existing code
def run_semantic_search(
    raw_query: str, 
    client: bigquery.Client, 
    distance_threshold: float = 0.8,
    top_k: int = 70,
    skip_classification: bool = False
) -> Dict[str, Any]:
    """
    Backward compatibility wrapper for existing code.
    Creates a default SearchConfig and SemanticSearchService.
    """
    if not client or not client.project:
        return {
            "success": False,
            "message": "Invalid BigQuery client",
            "results": None
        }
    
    config = SearchConfig(project_id=client.project)
    service = SemanticSearchService(config, client)
    
    return service.run_semantic_search(
        raw_query, distance_threshold, top_k, skip_classification
    )
