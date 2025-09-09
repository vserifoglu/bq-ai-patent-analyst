import os
import json
from dotenv import load_dotenv

load_dotenv()

# Try to access Streamlit secrets if available (works on Streamlit Cloud)
_SECRETS = None
try:
    import streamlit as st  # type: ignore
    _SECRETS = st.secrets
except Exception:
    _SECRETS = None


def _from_secrets(key: str, default=None):
    """Read a value from Streamlit secrets.
    Supports both top-level keys and a [default] section, returning default if not found.
    """
    if not _SECRETS:
        return default
    # Prefer top-level
    if key in _SECRETS:
        return _SECRETS.get(key, default)
    # Fallback to [default] section
    if "default" in _SECRETS and key in _SECRETS["default"]:
        return _SECRETS["default"].get(key, default)
    return default


def _get_bool(value, default=False):
    """Normalize truthy strings/bools to bool."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() == "true"
    return default

# App Metadata
APP_TITLE = os.getenv("APP_TITLE") or _from_secrets("APP_TITLE", "AI Patent Analyst")
APP_SUBTITLE = "Semantic Search for Patent Components"

# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT_ID") or _from_secrets("GOOGLE_CLOUD_PROJECT_ID")

# Ensure service account key is a JSON string; handle dicts from secrets by dumping to JSON
_GCP_SA_RAW = os.getenv("GCP_SA_KEY") or _from_secrets("GCP_SA_KEY")
if isinstance(_GCP_SA_RAW, dict):
    GCP_SA_KEY_JSON = json.dumps(_GCP_SA_RAW)
else:
    GCP_SA_KEY_JSON = _GCP_SA_RAW

BQ_LOCATION = os.getenv("BQ_LOCATION") or _from_secrets("BQ_LOCATION", "US")

# BigQuery Configuration
BQ_DATASET_ID = os.getenv("BQ_DATASET_ID") or _from_secrets("BQ_DATASET_ID")
BQ_TABLE_PATENT_KNOWLEDGE_GRAPH = os.getenv("BQ_TABLE_PATENT_KNOWLEDGE_GRAPH", "patent_knowledge_graph")

# Essential Constants
DEBUG_MODE = _get_bool(os.getenv("DEBUG_MODE") or _from_secrets("DEBUG_MODE", "False"), False)

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
