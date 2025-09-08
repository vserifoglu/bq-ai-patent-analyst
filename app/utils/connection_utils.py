"""Connection and environment utilities for BigQuery integration"""
from utils.gcp_auth import get_bigquery_client
from config.settings import (
    BQ_DATASET_ID, 
    BQ_TABLE_PATENT_KNOWLEDGE_GRAPH,
    GOOGLE_CLOUD_PROJECT_ID
)


def check_bigquery_connection(client=None):
    """Check BigQuery connection and return status"""
    try:
        client = client or get_bigquery_client()
        if not client:
            return False, "Failed to authenticate with GCP"

        # Test simple query
        query = "SELECT 1 as test"
        client.query(query).result()
        return True, "GCP connection successful"

    except Exception as e:
        return False, f"GCP connection failed: {str(e)}"


def get_app_stats(client=None):
    """Get basic statistics for the homepage"""
    try:
        client = client or get_bigquery_client()
        if not client:
            return _get_default_stats()

        # Combined query for better performance
        stats_query = f"""
        SELECT 
            COUNT(DISTINCT patent_id) as patent_count,
            COUNT(*) as component_count
        FROM `{GOOGLE_CLOUD_PROJECT_ID}.{BQ_DATASET_ID}.{BQ_TABLE_PATENT_KNOWLEDGE_GRAPH}`
        """

        result = client.query(stats_query).to_dataframe()
        row = result.iloc[0]

        return {
            "patent_count": int(row['patent_count']),
            "component_count": int(row['component_count']),
            "connection_status": "Connected to BigQuery"
        }

    except Exception:
        return _get_default_stats()


def _get_default_stats():
    """Return default statistics when BigQuery is not available"""
    return {
        "patent_count": 403,
        "component_count": 1000,
        "connection_status": "Using default values"
    }


def format_number(num):
    """Format numbers for display with commas"""
    if isinstance(num, int) and num >= 1000:
        return f"{num:,}"
    return str(num)


def validate_environment():
    """Validate that all required environment variables are set"""
    try:
        from config.settings import validate_config
        validate_config()
        return True, "Environment configuration is valid"
    except Exception as e:
        return False, str(e)
