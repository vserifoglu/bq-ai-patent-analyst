"""
Semantic Search Module for Patent Analysis
Simple implementation with independent, testable functions.
"""

from google.cloud import bigquery


def sanitize_for_sql(query: str) -> str:
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


def is_query_technical(search_query: str, client: bigquery.Client) -> bool:
    """
    Classify whether a query is technical using BigQuery ML.
    Independent function that doesn't call other functions.
    
    Args:
        search_query: The user's search query (should be sanitized externally)
        client: Authenticated BigQuery client
        
    Returns:
        True if query is technical, False otherwise
    """
    classification_prompt = f"""
        Is the following user query related to a technical, scientific, 
        or engineering topic? Answer with only 'Yes' or 'No'. Query: {search_query}
    """
    
    sql_query = f"""
    SELECT ml_generate_text_llm_result
    FROM ML.GENERATE_TEXT(
        MODEL `{client.project}.patent_analysis.gemini_vision_analyzer`,
        (SELECT '''{classification_prompt}''' AS prompt),
        STRUCT(
            0.0 AS temperature, 
            TRUE AS flatten_json_output, 
            1024 AS max_output_tokens
        )
    )
    """
    
    try:
        query_job = client.query(sql_query)
        results = query_job.result()
        for row in results:
            response = row.ml_generate_text_llm_result.strip().lower()
            if "yes" in response:
                return True
        return False
    except Exception as e:
        print(f"Error during query classification: {e}")
        return False


def perform_vector_search(
    search_query: str, 
    client: bigquery.Client, 
    distance_threshold: float = 0.8,
    top_k: int = 70
):
    """
    Perform vector search on patent components.
    Independent function that doesn't call other functions.
    
    Args:
        search_query: Sanitized search query
        client: Authenticated BigQuery client
        distance_threshold: Maximum cosine distance for results
        top_k: Number of top results to fetch
        
    Returns:
        DataFrame with search results or None if failed
    """
    sql_query = f"""
        WITH search_results AS (
          SELECT
            base.uri, base.component_name, base.component_function, distance
          FROM
            VECTOR_SEARCH(
              TABLE `{client.project}.patent_analysis.component_search_index`,
              'combined_vector',
              (
                SELECT ml_generate_embedding_result
                FROM ML.GENERATE_EMBEDDING(
                  MODEL `{client.project}.patent_analysis.embedding_model`,
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
    
    try:
        df = client.query(sql_query).to_dataframe()
        return df
    except Exception as e:
        print(f"Vector search failed: {e}")
        return None


def run_semantic_search(
    raw_query: str, 
    client: bigquery.Client, 
    distance_threshold: float = 0.8,
    top_k: int = 70,
    skip_classification: bool = False
):
    """
    Main orchestrator function that combines all search steps.
    Use this function in the dashboard.
    
    Args:
        raw_query: Raw user input
        client: Authenticated BigQuery client
        distance_threshold: Maximum cosine distance for results
        top_k: Number of top results to fetch
        skip_classification: Skip technical classification (useful for testing)
        
    Returns:
        Dictionary with success status, message, and results
    """
    # Step 1: Sanitize input
    sanitized_query = sanitize_for_sql(raw_query)
    
    if not sanitized_query:
        return {
            "success": False,
            "message": "Please enter a valid search query.",
            "results": None
        }
    
    # Step 2: Check if query is technical (unless skipped)
    if not skip_classification:
        is_technical = is_query_technical(sanitized_query, client)
        if not is_technical:
            return {
                "success": False,
                "message": "Query is not technical. Please enter a query related to a technical component or function.",
                "results": None
            }
    
    # Step 3: Perform vector search
    results_df = perform_vector_search(
        sanitized_query, 
        client, 
        distance_threshold=distance_threshold,
        top_k=top_k
    )
    
    if results_df is None:
        return {
            "success": False,
            "message": "Vector search failed. Please try again.",
            "results": None
        }
    
    if results_df.empty:
        return {
            "success": True,
            "message": f"No results found for '{raw_query}'. Try a different query.",
            "results": results_df
        }
    
    return {
        "success": True,
        "message": f"Found {len(results_df)} results for '{raw_query}'.",
        "results": results_df
    }
