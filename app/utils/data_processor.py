"""Data processing and transformation utilities with GCP integration"""
import streamlit as st
from utils.gcp_auth import get_bigquery_client
from config.settings import (
    BQ_DATASET_ID, 
    BQ_TABLE_PATENT_KNOWLEDGE_GRAPH,
    GOOGLE_CLOUD_PROJECT_ID
)

def test_gcp_connection():
    """Test GCP connection and return status"""
    try:
        client = get_bigquery_client()
        if not client:
            return False, "Failed to authenticate with GCP"
        
        # Test simple query
        query = "SELECT 1 as test"
        result = client.query(query).result()
        return True, "GCP connection successful"
        
    except Exception as e:
        return False, f"GCP connection failed: {str(e)}"

def get_app_stats():
    """Get basic statistics for the homepage"""
    try:
        client = get_bigquery_client()
        if not client:
            return get_default_stats()
        
        # Count patents
        patent_query = f"""
        SELECT COUNT(DISTINCT patent_id) as patent_count
        FROM `{GOOGLE_CLOUD_PROJECT_ID}.{BQ_DATASET_ID}.{BQ_TABLE_PATENT_KNOWLEDGE_GRAPH}`
        """
        
        # Count components
        component_query = f"""
        SELECT COUNT(*) as component_count
        FROM `{GOOGLE_CLOUD_PROJECT_ID}.{BQ_DATASET_ID}.{BQ_TABLE_PATENT_KNOWLEDGE_GRAPH}`
        """
        
        patent_result = client.query(patent_query).to_dataframe()
        component_result = client.query(component_query).to_dataframe()
        
        return {
            "patent_count": int(patent_result.iloc[0]['patent_count']),
            "component_count": int(component_result.iloc[0]['component_count']),
            "connection_status": "Connected to BigQuery"
        }
        
    except Exception as e:
        return get_default_stats()

def get_default_stats():
    """Return default statistics when BigQuery is not available"""
    return {
        "patent_count": 403,
        "component_count": "1000+",
        "connection_status": "Using default values"
    }

def format_number(num):
    """Format numbers for display"""
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
