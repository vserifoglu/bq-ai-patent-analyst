"""Google Cloud Platform authentication and BigQuery client setup"""
import json
import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account
from config.settings import (
    GOOGLE_CLOUD_PROJECT_ID, 
    GCP_SA_KEY_JSON, 
    BQ_LOCATION,
    validate_config
)

class GCPAuth:
    """Handle GCP authentication similar to Kaggle notebook setup"""
    
    def __init__(self):
        self.project_id = GOOGLE_CLOUD_PROJECT_ID
        self.location = BQ_LOCATION
        self.credentials = None
        self.client = None
        
    def authenticate(self):
        """Authenticate with GCP using service account key from environment"""
        try:
            # Validate configuration
            validate_config()
            
            # Parse the service account key JSON
            sa_key_dict = json.loads(GCP_SA_KEY_JSON)
            
            # Create credentials from service account info
            self.credentials = service_account.Credentials.from_service_account_info(sa_key_dict)
            
            # Create BigQuery client
            self.client = bigquery.Client(
                credentials=self.credentials,
                project=self.project_id,
                location=self.location
            )
            
            return True
            
        except Exception as e:
            return False
    
    def get_client(self):
        """Get authenticated BigQuery client"""
        if not self.client:
            if not self.authenticate():
                return None
        return self.client

# Global instance
@st.cache_resource
def get_bigquery_client():
    """Get cached BigQuery client"""
    auth = GCPAuth()
    return auth.get_client()
