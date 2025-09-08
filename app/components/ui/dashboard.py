import streamlit as st

from components.ui.semantic_search_tab import SemanticSearchTabUI
from components.ui.data_visualization_tab import DataVisualizationTabUI


class DashboardUI:
    """Dashboard UI Coordinator - combines tab components"""

    def __init__(self):
        """Initialize with tab UI components"""
        self.semantic_search_tab = SemanticSearchTabUI()
        self.data_viz_tab = DataVisualizationTabUI()
    
    def render_home_overview_mode(self) -> dict:
        """Render home tab in overview mode"""
        self.semantic_search_tab.render_project_narrative()
        st.markdown("---")
        return self.semantic_search_tab.render_search_box()
    
    def render_home_search_mode(self, query: str, results_df=None, 
                              message: str = "", success: bool = False) -> dict:
        """Render home tab in search mode"""
        search_actions = self.semantic_search_tab.render_search_box(query)
        st.markdown("---")
        
        if results_df is not None or message:
            self.semantic_search_tab.render_search_results(results_df, message, success)
        
        return search_actions
    
    def render_data_tab_disconnected(self, gcp_message: str):
        """Render data tab when BigQuery is not connected"""
        self.data_viz_tab.render_connection_warning(gcp_message)
        self.data_viz_tab.render_visualization_placeholder()
    
    def render_data_tab_connected_progressive(self):
        """Render data tab with progressive loading - complete sections at once"""
        # Create placeholders for each complete section
        portfolio_section = st.empty()
        distribution_section = st.empty() 
        outlier_section = st.empty()
        
        return {
            'portfolio_section': portfolio_section,
            'distribution_section': distribution_section,
            'outlier_section': outlier_section
        }
