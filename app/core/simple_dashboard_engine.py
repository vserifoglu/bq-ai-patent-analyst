"""Simplified Dashboard Engine for Clean UI Architecture"""
import streamlit as st

from core.app_controller import AppController
from core.state_manager import StateManager
from components.ui.dashboard import DashboardUI
from core.models import SearchRequest


class SimpleDashboardEngine:
    """Simplified engine that coordinates between business logic and clean UI"""
    
    def __init__(self, controller: AppController, state_manager: StateManager):
        """Initialize with dependencies"""
        self.controller = controller
        self.state = state_manager
        self.ui = DashboardUI()
    
    def run(self):
        """Main orchestration method - clean UI without technical details"""
        # Load main content immediately
        if self.state.is_search_triggered():
            self._handle_search_mode()
        else:
            self._handle_overview_mode()
    
    def _handle_overview_mode(self):
        """Handle overview mode display"""
        search_actions = self.ui.render_home_overview_mode()
        
        # Handle search button click
        if search_actions['search_clicked'] and search_actions['query']:
            self.state.trigger_search(search_actions['query'])
            st.rerun()
    
    def _handle_search_mode(self):
        """Handle search mode display"""
        query = self.state.get_search_query()
        
        # Get search results
        search_data = self._get_search_results(query)
        
        # Render search mode UI
        search_actions = self.ui.render_home_search_mode(
            query=query,
            results_df=search_data.get('display_df'),
            message=search_data.get('message', ''),
            success=search_data.get('success', False)
        )
        
        # Handle new search
        if search_actions['search_clicked'] and search_actions['query']:
            if search_actions['query'] != query:  # New query
                self.state.trigger_search(search_actions['query'])
                st.rerun()
    
    def run_data_tab(self):
        """Handle data visualization tab with progressive loading"""
        # Quick connection check for main content (hidden from user)
        try:
            status = self.controller.get_connection_status()
            
            if not status.gcp_connected:
                st.warning("🔗 Data visualization requires BigQuery connection")
                st.info("💡 Configure your environment to see real visualizations.")
                self._render_visualization_placeholder()
            else:
                # Set up section placeholders
                sections = self.ui.render_data_tab_connected_progressive()
                
                # Load complete sections progressively
                self._load_portfolio_section(sections['portfolio_section'])
                self._load_distribution_section(sections['distribution_section'])
                self._load_outlier_section(sections['outlier_section'])
        except Exception as e:
            st.error("Unable to load data visualizations at this time.")
            st.info("Please try again later.")
    
    def _render_visualization_placeholder(self):
        """Display visualization placeholder when not connected"""
        st.markdown("#### Preview Layout")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Left Column:** Component Distribution Histogram")
            st.container(height=200, border=True)
        
        with col2:
            st.markdown("**Right Column:** Strategic Portfolio Analysis")
            st.container(height=200, border=True)
    
    def _load_portfolio_section(self, section_placeholder):
        """Load complete portfolio section with header, chart, and explanation"""
        with section_placeholder.container():
            with st.spinner("Loading strategic portfolio analysis..."):
                try:
                    success, message, chart_result = self.controller.get_formatted_portfolio_chart_data()
                    
                    # Show complete section once data is ready
                    self.ui.data_viz_tab.render_strategic_insights_header()
                    
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        if success and chart_result and chart_result.get('has_plotly'):
                            st.plotly_chart(chart_result['figure'], use_container_width=True)
                            st.success(f"✅ {message}")
                        else:
                            st.error(f"❌ Portfolio analysis failed: {message}")
                    
                    with col2:
                        self.ui.data_viz_tab.render_portfolio_explanation()
                    
                    st.markdown("---")
                    
                except Exception as e:
                    st.error(f"❌ Portfolio section error: {str(e)}")
    
    def _load_distribution_section(self, section_placeholder):
        """Load complete distribution section with header, chart, and explanation"""
        with section_placeholder.container():
            with st.spinner("Loading component distribution analysis..."):
                try:
                    success, message, chart_result = self.controller.get_formatted_distribution_chart_data()
                    
                    # Show complete section once data is ready
                    self.ui.data_viz_tab.render_component_analysis_header()
                    
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        if success and chart_result and chart_result.get('has_plotly'):
                            st.plotly_chart(chart_result['figure'], use_container_width=True)
                            st.success(f"✅ {message}")
                        else:
                            st.error(f"❌ Distribution analysis failed: {message}")
                    
                    with col2:
                        self.ui.data_viz_tab.render_distribution_explanation()
                    
                    st.markdown("---")
                    
                except Exception as e:
                    st.error(f"❌ Distribution section error: {str(e)}")
    
    def _load_outlier_section(self, section_placeholder):
        """Load complete outlier section"""
        with section_placeholder.container():
            with st.spinner("Performing outlier detection analysis..."):
                try:
                    success, message, outliers_df = self.controller.get_formatted_component_outliers()
                    
                    # Show complete section once data is ready
                    st.markdown("**Component Count Outlier Detection**")
                    
                    if success:
                        if outliers_df is not None and not outliers_df.empty:
                            st.warning(f"⚠️ {message}")
                            st.dataframe(
                                outliers_df,
                                use_container_width=True,
                                hide_index=True
                            )
                        else:
                            st.success(f"✅ {message}")
                    else:
                        st.error(f"❌ Outlier detection failed: {message}")
                        
                except Exception as e:
                    st.error(f"❌ Outlier section error: {str(e)}")
    
    def _get_search_results(self, query: str) -> dict:
        """Get search results and format for UI"""
        try:
            request = SearchRequest(query=query)
            response = self.controller.search_patents(request)
            
            if response.success and response.results:
                display_df = self.controller.format_search_results_for_display(response)
                return {
                    'success': True,
                    'message': response.message,
                    'display_df': display_df
                }
            else:
                return {
                    'success': response.success,
                    'message': response.message,
                    'display_df': None
                }
        except Exception as e:
            return {
                'success': False,
                'message': f"Search error: {str(e)}",
                'display_df': None
            }
