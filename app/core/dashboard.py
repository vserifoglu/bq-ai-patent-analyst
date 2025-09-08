import streamlit as st

from core.app_controller import AppController
from core.interfaces.state_interface import StateInterface
from components.ui.dashboard import DashboardUI
from core.models import SearchRequest


class DashboardEngine:
    """Dashboard engine that coordinates between business logic and clean UI"""
    
    def __init__(self, controller: AppController, state_manager: StateInterface):
        """Initialize with dependencies"""
        self.controller = controller
        self.state = state_manager
        self.ui = DashboardUI()
    
    def run(self):
        """Main orchestration method - clean UI without technical details"""
        # Get business data first
        if self.state.is_search_triggered():
            query = self.state.get_search_query()
            search_data = self._get_search_mode_data(query)
            self._render_search_mode_ui(query, search_data)
        else:
            overview_data = self._get_overview_mode_data()
            self._render_overview_mode_ui(overview_data)
    
    def _get_overview_mode_data(self) -> dict:
        """Pure business logic for overview mode"""
        return {
            'mode': 'overview',
            'ready_for_search': True
        }
    
    def _get_search_mode_data(self, query: str) -> dict:
        """Pure business logic for search mode-"""
        search_data = self._get_search_results(query)
        return {
            'mode': 'search',
            'query': query,
            'display_df': search_data.get('display_df'),
            'message': search_data.get('message', ''),
            'success': search_data.get('success', False)
        }
    
    def _get_visualization_data(self) -> dict:
        """Pure business logic for visualization data-"""
        try:
            status = self.controller.get_connection_status()
            
            if not status.gcp_connected:
                return {
                    'connected': False,
                    'message': status.gcp_message,
                    'show_placeholder': True
                }
            
            # Get all visualization data
            portfolio_result = self.controller.get_formatted_portfolio_chart_data()
            distribution_result = self.controller.get_formatted_distribution_chart_data()
            outlier_result = self.controller.get_formatted_component_outliers()
            
            return {
                'connected': True,
                'portfolio': {
                    'success': portfolio_result[0],
                    'message': portfolio_result[1],
                    'data': portfolio_result[2]
                },
                'distribution': {
                    'success': distribution_result[0],
                    'message': distribution_result[1],
                    'data': distribution_result[2]
                },
                'outliers': {
                    'success': outlier_result[0],
                    'message': outlier_result[1],
                    'data': outlier_result[2]
                }
            }
        except Exception as e:
            return {
                'connected': False,
                'error': str(e),
                'show_error': True
            }

    # ===== UI RENDERING METHODS (STREAMLIT-SPECIFIC) =====
    
    def _render_overview_mode_ui(self, data: dict):
        """Handle overview mode UI rendering"""
        search_actions = self.ui.render_home_overview_mode()
        
        # Handle search button click
        if search_actions['search_clicked'] and search_actions['query']:
            self.state.trigger_search(search_actions['query'])
            st.rerun()

    def _render_search_mode_ui(self, query: str, data: dict):
        """Handle search mode UI rendering"""
        # Render search mode UI
        search_actions = self.ui.render_home_search_mode(
            query=query,
            results_df=data.get('display_df'),
            message=data.get('message', ''),
            success=data.get('success', False)
        )
        
        # Handle new search
        if search_actions['search_clicked'] and search_actions['query']:
            if search_actions['query'] != query:  # New query
                self.state.trigger_search(search_actions['query'])
                st.rerun()
    
    def run_data_tab(self):
        """Handle data visualization tab with progressive loading"""
        # Get business data first
        viz_data = self._get_visualization_data()
        
        # Render UI based on data
        self._render_data_tab_ui(viz_data)
    
    def _render_data_tab_ui(self, data: dict):
        """Render data tab UI based on business data"""
        if not data.get('connected', False):
            if data.get('show_error', False):
                st.error("Unable to load data visualizations at this time.")
                st.info("Please try again later.")
            else:
                st.warning("🔗 Data visualization requires BigQuery connection")
                st.info("💡 Configure your environment to see real visualizations.")
                self._render_visualization_placeholder()
        else:
            # Set up section placeholders
            sections = self.ui.render_data_tab_connected_progressive()
            
            # Load complete sections progressively
            self._load_portfolio_section_ui(sections['portfolio_section'], data['portfolio'])
            self._load_distribution_section_ui(sections['distribution_section'], data['distribution'])
            self._load_outlier_section_ui(sections['outlier_section'], data['outliers'])
    
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
    
    def _load_portfolio_section_ui(self, section_placeholder, portfolio_data: dict):
        """Load complete portfolio section UI with data"""
        with section_placeholder.container():
            with st.spinner("Loading strategic portfolio analysis..."):
                try:
                    # Show complete section once data is ready
                    self.ui.data_viz_tab.render_strategic_insights_header()
                    
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        if portfolio_data['success'] and portfolio_data['data'] and portfolio_data['data'].get('has_plotly'):
                            st.plotly_chart(portfolio_data['data']['figure'], use_container_width=True)
                            st.success(f"✅ {portfolio_data['message']}")
                        else:
                            st.error(f"❌ Portfolio analysis failed: {portfolio_data['message']}")
                    
                    with col2:
                        self.ui.data_viz_tab.render_portfolio_explanation()
                    
                    st.markdown("---")
                    
                except Exception as e:
                    st.error(f"❌ Portfolio section error: {str(e)}")
    
    def _load_distribution_section_ui(self, section_placeholder, distribution_data: dict):
        """Load complete distribution section UI with data"""
        with section_placeholder.container():
            with st.spinner("Loading component distribution analysis..."):
                try:
                    # Show complete section once data is ready
                    self.ui.data_viz_tab.render_component_analysis_header()
                    
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        if distribution_data['success'] and distribution_data['data'] and distribution_data['data'].get('has_plotly'):
                            st.plotly_chart(distribution_data['data']['figure'], use_container_width=True)
                            st.success(f"✅ {distribution_data['message']}")
                        else:
                            st.error(f"❌ Distribution analysis failed: {distribution_data['message']}")
                    
                    with col2:
                        self.ui.data_viz_tab.render_distribution_explanation()
                    
                    st.markdown("---")
                    
                except Exception as e:
                    st.error(f"❌ Distribution section error: {str(e)}")
    
    def _load_outlier_section_ui(self, section_placeholder, outlier_data: dict):
        """Load complete outlier section UI with data"""
        with section_placeholder.container():
            with st.spinner("Performing outlier detection analysis..."):
                try:
                    # Show complete section once data is ready
                    st.markdown("**Component Count Outlier Detection**")
                    
                    if outlier_data['success']:
                        if outlier_data['data'] is not None and not outlier_data['data'].empty:
                            st.warning(f"⚠️ {outlier_data['message']}")
                            st.dataframe(
                                outlier_data['data'],
                                use_container_width=True,
                                hide_index=True
                            )
                        else:
                            st.success(f"✅ {outlier_data['message']}")
                    else:
                        st.error(f"❌ Outlier detection failed: {outlier_data['message']}")
                        
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
