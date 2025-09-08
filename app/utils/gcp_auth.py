"""Google Cloud Platform authentication and BigQuery client setup"""
import json
import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account
from typing import Optional, Dict, Any
from config.settings import (
    GOOGLE_CLOUD_PROJECT_ID, 
    GCP_SA_KEY_JSON, 
    BQ_LOCATION,
    validate_config
)

class GCPAuth:
    """Handle GCP authentication similar to Kaggle notebook setup"""
    
    def __init__(
            self, 
            project_id: Optional[str] = None, 
            location: Optional[str] = None, 
            sa_key_json: Optional[str] = None, 
            config_validator: Optional[callable] = None
        ):
        """Initialize with optional dependency injection for testing"""
        self.project_id = project_id or GOOGLE_CLOUD_PROJECT_ID
        self.location = location or BQ_LOCATION
        self.sa_key_json = sa_key_json or GCP_SA_KEY_JSON
        self.config_validator = config_validator or validate_config
        self.credentials = None
        self.client = None
        
    def authenticate(self) -> tuple[bool, Optional[str]]:
        """Authenticate with GCP using service account key from environment
        
        Returns:
            tuple: (success: bool, error_message: Optional[str])
        """
        try:
            # Validate configuration
            self.config_validator()
            
            # Parse the service account key JSON
            sa_key_dict = self._parse_service_account_key(self.sa_key_json)
            
            # Create credentials from service account info
            self.credentials = self._create_credentials(sa_key_dict)
            
            # Create BigQuery client
            self.client = self._create_bigquery_client()
            
            return True, None
            
        except Exception as e:
            return False, str(e)
    
    def _parse_service_account_key(self, sa_key_json: str) -> Dict[str, Any]:
        """Parse service account key JSON - extracted for testing"""
        return json.loads(sa_key_json)
    
    def _create_credentials(self, sa_key_dict: Dict[str, Any]):
        """Create credentials from service account dict - extracted for testing"""
        return service_account.Credentials.from_service_account_info(sa_key_dict)
    
    def _create_bigquery_client(self):
        """Create BigQuery client - extracted for testing"""
        return bigquery.Client(
            credentials=self.credentials,
            project=self.project_id,
            location=self.location
        )
    
    def get_client(self) -> Optional[bigquery.Client]:
        """Get authenticated BigQuery client
        
        Returns:
            Optional[bigquery.Client]: Authenticated client or None if authentication failed
        """
        if not self.client:
            success, error = self.authenticate()
            if not success:
                return None
        return self.client
    
    def is_authenticated(self) -> bool:
        """Check if authentication is successful"""
        return self.client is not None and self.credentials is not None
    
    def reset(self):
        """Reset authentication state - useful for testing"""
        self.credentials = None
        self.client = None

# Global instance - separated for better testing
def create_gcp_auth() -> GCPAuth:
    """Factory function to create GCPAuth instance"""
    return GCPAuth()

@st.cache_resource
def get_bigquery_client() -> Optional[bigquery.Client]:
    """Get cached BigQuery client"""
    auth = create_gcp_auth()
    return auth.get_client()
