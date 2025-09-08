"""Visualization service for data processing - handles BigQuery execution"""
import sys
import os
import pandas as pd
from typing import Tuple, Optional

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.visualization_queries import (
    get_outlier_detection_query,
    get_component_distribution_query,
    get_portfolio_analysis_query
)


def detect_component_outliers(client, project_id: str) -> Tuple[bool, str, Optional[pd.DataFrame]]:
    """
    Detect patents with anomalous number of components
    Returns: (success, message, dataframe)
    """
    try:
        query = get_outlier_detection_query(project_id)
        df_outliers = client.query(query).to_dataframe()
        
        if df_outliers.empty:
            return True, "No significant outliers found in component counts.", df_outliers
        else:
            message = f"Found {len(df_outliers)} patents with unusually high number of components."
            return True, message, df_outliers
            
    except Exception as e:
        return False, f"Outlier detection failed: {str(e)}", None


def get_component_distribution_data(client, project_id: str) -> Tuple[bool, str, Optional[pd.DataFrame]]:
    """
    Get component count distribution data for histogram
    Returns: (success, message, dataframe)
    """
    try:
        query = get_component_distribution_query(project_id)
        df_distribution = client.query(query).to_dataframe()
        
        if df_distribution.empty:
            return False, "No component distribution data found.", None
        else:
            message = f"Retrieved component distribution for {len(df_distribution)} patents."
            return True, message, df_distribution
            
    except Exception as e:
        return False, f"Component distribution query failed: {str(e)}", None


def get_portfolio_analysis_data(client, project_id: str) -> Tuple[bool, str, Optional[pd.DataFrame]]:
    """
    Get strategic patent portfolio analysis data for bubble chart
    Returns: (success, message, dataframe)
    """
    try:
        query = get_portfolio_analysis_query(project_id)
        df_portfolio = client.query(query).to_dataframe()
        
        if df_portfolio.empty:
            return False, "No portfolio analysis data found.", None
        else:
            message = f"Retrieved portfolio analysis for {len(df_portfolio)} applicants."
            return True, message, df_portfolio
            
    except Exception as e:
        return False, f"Portfolio analysis query failed: {str(e)}", None
