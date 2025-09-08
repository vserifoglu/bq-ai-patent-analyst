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

    def render_data_tab_connected(self, portfolio: dict, distribution: dict, outliers: dict):
        """Render data tab when connected, delegating section rendering with spinners"""
        sections = self.render_data_tab_connected_progressive()

        # Portfolio section
        with sections['portfolio_section'].container():
            with st.spinner("Loading strategic portfolio analysis..."):
                try:
                    self.data_viz_tab.render_strategic_insights_header()
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        if portfolio.get('success') and portfolio.get('data') and portfolio['data'].get('has_plotly'):
                            st.plotly_chart(portfolio['data']['figure'], use_container_width=True)
                            if portfolio.get('message'):
                                st.success(f"✅ {portfolio['message']}")
                        else:
                            st.error(f"❌ Portfolio analysis failed: {portfolio.get('message', 'No message')}")
                    with col2:
                        self.data_viz_tab.render_portfolio_explanation()
                    st.markdown("---")
                except Exception as e:
                    st.error(f"❌ Portfolio section error: {str(e)}")

        # Distribution section
        with sections['distribution_section'].container():
            with st.spinner("Loading component distribution analysis..."):
                try:
                    self.data_viz_tab.render_component_analysis_header()
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        if distribution.get('success') and distribution.get('data') and distribution['data'].get('has_plotly'):
                            st.plotly_chart(distribution['data']['figure'], use_container_width=True)
                            if distribution.get('message'):
                                st.success(f"✅ {distribution['message']}")
                        else:
                            st.error(f"❌ Distribution analysis failed: {distribution.get('message', 'No message')}")
                    with col2:
                        self.data_viz_tab.render_distribution_explanation()
                    st.markdown("---")
                except Exception as e:
                    st.error(f"❌ Distribution section error: {str(e)}")

        # Outlier section
        with sections['outlier_section'].container():
            with st.spinner("Performing outlier detection analysis..."):
                try:
                    st.markdown("**Component Count Outlier Detection**")
                    if outliers.get('success'):
                        df_out = outliers.get('data')
                        msg = outliers.get('message', '')
                        if df_out is not None and hasattr(df_out, 'empty') and not df_out.empty:
                            st.warning(f"⚠️ {msg}")
                            st.dataframe(df_out, use_container_width=True, hide_index=True)
                        else:
                            st.success(f"✅ {msg}")
                    else:
                        st.error(f"❌ Outlier detection failed: {outliers.get('message', 'No message')}")
                except Exception as e:
                    st.error(f"❌ Outlier section error: {str(e)}")
