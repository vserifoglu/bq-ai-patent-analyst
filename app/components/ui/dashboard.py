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
            # ROI section (static, lightweight)
            self.data_viz_tab.render_roi_section()
            st.markdown("---")
            with st.spinner("Loading strategic portfolio analysis..."):
                try:
                    self.data_viz_tab.render_strategic_insights_header()
                    if portfolio.get('success') and portfolio.get('data') and portfolio['data'].get('has_plotly'):
                        st.plotly_chart(portfolio['data']['figure'], use_container_width=True)
                        st.caption("Key Insight: Companies in the top-right quadrant demonstrate both diverse and highly complex patent portfolios.")
                        if portfolio.get('message'):
                            st.success(f"✅ {portfolio['message']}")
                    else:
                        st.error(f"❌ Portfolio analysis failed: {portfolio.get('message', 'No message')}")
                    st.markdown("---")
                except Exception as e:
                    st.error(f"❌ Portfolio section error: {str(e)}")

        # Distribution section
        with sections['distribution_section'].container():
            with st.spinner("Loading component distribution analysis..."):
                try:
                    st.subheader("Invention Complexity Analysis")
                    if distribution.get('success') and distribution.get('data') and distribution['data'].get('has_plotly'):
                        st.plotly_chart(distribution['data']['figure'], use_container_width=True)
                        st.caption("""
                        Key Insight: The distribution shows that most patents are of low-to-medium complexity (2-10 components). The long tail of outliers corresponds to inventions with detailed technical diagrams, proving that our multimodal analysis is essential for capturing true architectural complexity.
                        """)
                        if distribution.get('message'):
                            st.success(f"✅ {distribution['message']}")
                    else:
                        st.error(f"❌ Distribution analysis failed: {distribution.get('message', 'No message')}")
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
                            # Render with clickable link if 'Open' URL column present
                            col_cfg = None
                            try:
                                if 'Open' in df_out.columns:
                                    col_cfg = {
                                        'Open': st.column_config.LinkColumn(
                                            'Open',
                                            help='Open the PDF in a new tab',
                                            display_text='open patent ↗'
                                        )
                                    }
                            except Exception:
                                col_cfg = None
                            st.dataframe(df_out, use_container_width=True, hide_index=True, column_config=col_cfg)
                        else:
                            st.success(f"✅ {msg}")
                    else:
                        st.error(f"❌ Outlier detection failed: {outliers.get('message', 'No message')}")
                except Exception as e:
                    st.error(f"❌ Outlier section error: {str(e)}")

    def run_with_spinner(self, target, message: str, fn):
        """Run a callable within a spinner tied to a placeholder; return its result.
        Expects fn to return either a tuple or a single value.
        """
        with target.container():
            with st.spinner(message):
                return fn()

    # --- Progressive section helpers used by engine.run_data_tab ---
    def render_portfolio_section_loading(self, target):
        with target.container():
            with st.spinner("Loading strategic portfolio analysis..."):
                self.data_viz_tab.render_strategic_insights_header()
                st.empty()

    def render_distribution_section_loading(self, target):
        with target.container():
            with st.spinner("Loading component distribution analysis..."):
                self.data_viz_tab.render_component_analysis_header()
                st.empty()

    def render_outlier_section_loading(self, target):
        with target.container():
            with st.spinner("Performing outlier detection analysis..."):
                st.markdown("**Component Count Outlier Detection**")
                st.empty()

    def render_portfolio_section(self, target, portfolio: dict):
        with target.container():
            try:
                # ROI section (static, lightweight)
                self.data_viz_tab.render_roi_section()
                st.markdown("---")
                self.data_viz_tab.render_strategic_insights_header()
                if portfolio.get('success') and portfolio.get('data') and portfolio['data'].get('has_plotly'):
                    st.plotly_chart(portfolio['data']['figure'], use_container_width=True)
                    st.caption("Key Insight: Companies in the top-right quadrant demonstrate both diverse and highly complex patent portfolios.")
                    if portfolio.get('message'):
                        st.success(f"✅ {portfolio['message']}")
                else:
                    st.error(f"❌ Portfolio analysis failed: {portfolio.get('message', 'No message')}")
                st.markdown("---")
            except Exception as e:
                st.error(f"❌ Portfolio section error: {str(e)}")

    def render_distribution_section(self, target, distribution: dict):
        with target.container():
            try:
                st.subheader("Invention Complexity Analysis")
                if distribution.get('success') and distribution.get('data') and distribution['data'].get('has_plotly'):
                    st.plotly_chart(distribution['data']['figure'], use_container_width=True)
                    st.caption("""
                    Key Insight: The distribution shows that most patents are of low-to-medium complexity (2-10 components). The long tail of outliers corresponds to inventions with detailed technical diagrams, proving that our multimodal analysis is essential for capturing true architectural complexity.
                    """)
                    if distribution.get('message'):
                        st.success(f"✅ {distribution['message']}")
                else:
                    st.error(f"❌ Distribution analysis failed: {distribution.get('message', 'No message')}")
                st.markdown("---")
            except Exception as e:
                st.error(f"❌ Distribution section error: {str(e)}")

    def render_outlier_section(self, target, outliers: dict):
        with target.container():
            try:
                st.markdown("**Component Count Outlier Detection**")
                if outliers.get('success'):
                    df_out = outliers.get('data')
                    msg = outliers.get('message', '')
                    if df_out is not None and hasattr(df_out, 'empty') and not df_out.empty:
                        st.warning(f"⚠️ {msg}")
                        # Render with clickable link if 'Open' URL column present
                        col_cfg = None
                        try:
                            if 'Open' in df_out.columns:
                                col_cfg = {
                                    'Open': st.column_config.LinkColumn(
                                        'Open',
                                        help='Open the PDF in a new tab',
                                        display_text='open patent ↗'
                                    )
                                }
                        except Exception:
                            col_cfg = None
                        st.dataframe(df_out, use_container_width=True, hide_index=True, column_config=col_cfg)
                    else:
                        st.success(f"✅ {msg}")
                else:
                    st.error(f"❌ Outlier detection failed: {outliers.get('message', 'No message')}")
            except Exception as e:
                st.error(f"❌ Outlier section error: {str(e)}")

    def render_section_error(self, target, message: str):
        with target.container():
            st.error(message)
