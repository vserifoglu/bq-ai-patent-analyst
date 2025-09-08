import os
import json
from dotenv import load_dotenv

load_dotenv()

# App Metadata
APP_TITLE = os.getenv("APP_TITLE", "AI Patent Analyst")
APP_SUBTITLE = "Semantic Search for Patent Components"

# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
GCP_SA_KEY_JSON = os.getenv("GCP_SA_KEY")
BQ_LOCATION = os.getenv("BQ_LOCATION", "US")

# BigQuery Configuration
BQ_DATASET_ID = os.getenv("BQ_DATASET_ID")
BQ_TABLE_PATENT_KNOWLEDGE_GRAPH = os.getenv("BQ_TABLE_PATENT_KNOWLEDGE_GRAPH", "patent_knowledge_graph")

# Essential Constants
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"

# Validation function
def validate_config():
    """Validate required configuration"""
    required_vars = [
        ("GOOGLE_CLOUD_PROJECT_ID", GOOGLE_CLOUD_PROJECT_ID),
        ("GCP_SA_KEY", GCP_SA_KEY_JSON),
        ("BQ_DATASET_ID", BQ_DATASET_ID)
    ]
    
    missing_vars = [var_name for var_name, var_value in required_vars if not var_value]
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    # Validate JSON format of service account key
    if GCP_SA_KEY_JSON:
        try:
            json.loads(GCP_SA_KEY_JSON)
        except json.JSONDecodeError:
            raise ValueError("GCP_SA_KEY must be valid JSON")
    
    return True
