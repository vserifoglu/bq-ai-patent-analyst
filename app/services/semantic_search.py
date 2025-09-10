"""
Semantic Search Module for Patent Analysis
Simple implementation with independent, testable functions.
"""

from google.cloud import bigquery
from typing import Optional, Tuple
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

    def _build_grouped_search_query(
            self,
            search_query: str,
            distance_threshold: float,
            top_k: int,
            patents_limit: int = 20,
            per_uri_limit: int = 5,
    ) -> str:
            """Build SQL for grouped-by-patent results with top components per URI."""
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
                    SELECT
                        uri,
                        MIN(distance) AS best_distance,
                        COUNT(1) AS hit_count,
                        ARRAY_AGG(STRUCT(component_name, component_function, distance) ORDER BY distance ASC LIMIT {per_uri_limit}) AS top_components
                    FROM search_results
                    WHERE distance < {distance_threshold}
                    GROUP BY uri
                    ORDER BY best_distance ASC
                    LIMIT {patents_limit}
            """

    def _build_detail_query(
            self,
            search_query: str,
            uri: str,
            distance_threshold: float,
            top_k: int,
    ) -> str:
            """Build SQL to fetch all component hits for a specific patent URI."""
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
                    SELECT uri, component_name, component_function, distance
                    FROM search_results
                    WHERE distance < {distance_threshold} AND uri = '{uri}'
                    ORDER BY distance ASC
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

    def perform_grouped_search(
        self,
        sanitized_query: str,
        distance_threshold: float = 0.8,
        top_k: int = 70,
        patents_limit: int = 20,
        per_uri_limit: int = 5,
    ) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
        """Run grouped-by-patent search and return aggregated rows per URI.

        Expects pre-sanitized query text (controller sanitizes before calling).
        """
        if not self.client:
            return None, "BigQuery client not available"

        if not sanitized_query:
            return None, "Please enter a valid search query."

        sql_query = self._build_grouped_search_query(
            sanitized_query,
            distance_threshold=distance_threshold,
            top_k=top_k,
            patents_limit=patents_limit,
            per_uri_limit=per_uri_limit,
        )
        try:
            df = self.client.query(sql_query).to_dataframe()
            return df, None
        except Exception as e:
            return None, f"Grouped search failed: {str(e)}"

    def get_components_for_uri(
        self,
        sanitized_query: str,
        sanitized_uri: str,
        distance_threshold: float = 0.8,
        top_k: int = 70,
    ) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
        """Fetch detailed component hits for a given patent URI.

        Expects pre-sanitized inputs (controller sanitizes before calling).
        """
        if not self.client:
            return None, "BigQuery client not available"

        if not sanitized_query or not sanitized_uri:
            return None, "Invalid query or URI."

        sql_query = self._build_detail_query(
            sanitized_query, sanitized_uri, distance_threshold=distance_threshold, top_k=top_k
        )
        try:
            df = self.client.query(sql_query).to_dataframe()
            return df, None
        except Exception as e:
            return None, f"Detail fetch failed: {str(e)}"
    
    def run_semantic_search(
        self,
        raw_query: str,
        distance_threshold: float = 0.8,
        top_k: int = 70,
        skip_classification: bool = False,
    ) -> Tuple[bool, str, Optional[pd.DataFrame]]:
        """
        Main orchestrator function that combines all search steps.

        Args:
            raw_query: Raw user input
            distance_threshold: Maximum cosine distance for results
            top_k: Number of top results to fetch
            skip_classification: Skip technical classification (useful for testing)

        Returns:
            Tuple of (success, message, results_df)
        """
        # Step 1: Sanitize input
        sanitized_query = self.sanitize_for_sql(raw_query)
        
        if not sanitized_query:
            return False, "Please enter a valid search query.", None
        
        # Step 2: Check if query is technical (unless skipped)
        # if not skip_classification:
        #     is_technical, error = self.is_query_technical(sanitized_query)
        #     if error:
        #         return {
        #             "success": False,
        #             "message": f"Classification failed: {error}",
        #             "results": None
        #         }
        #     if not is_technical:
        #         return {
        #             "success": False,
        #             "message": "Query is not technical. Please enter a query related to a technical component or function.",
        #             "results": None
        #         }
        
        # Step 3: Perform vector search
        results_df, error = self.perform_vector_search(
            sanitized_query, 
            distance_threshold=distance_threshold,
            top_k=top_k
        )
        
        if error:
            return False, error, None
        
        if results_df is None or results_df.empty:
            return True, f"No results found for '{raw_query}'. Try a different query.", results_df or pd.DataFrame()

        return True, f"Found {len(results_df)} results for '{raw_query}'.", results_df
