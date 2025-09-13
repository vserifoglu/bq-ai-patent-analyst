from core.app_controller import AppController
from core.interfaces.state_interface import StateInterface
from components.ui.dashboard import DashboardUI
from core.models import SearchRequest
import pandas as pd


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

    # ===== UI RENDERING METHODS (Delegated to UI layer) =====
    
    def _render_overview_mode_ui(self, data: dict):
        """Handle overview mode UI rendering"""
        search_actions = self.ui.render_home_overview_mode()
        
        # Handle search button click
        if search_actions['search_clicked'] and search_actions['query']:
            # Trigger search; Streamlit rerun handled by the state adapter in production
            self.state.trigger_search(search_actions['query'])

    def _render_search_mode_ui(self, query: str, data: dict):
        """Handle search mode UI rendering"""
        # Render search box (no results yet)
        search_actions = self.ui.render_home_search_mode(
            query=query,
            results_df=None,
            message="",
            success=True,
        )
        # Use the most recent query immediately if user clicked an example or Search
        active_query = (
            search_actions.get('query')
            if search_actions.get('search_clicked') and search_actions.get('query')
            else query
        )
        # Grouped view toggle handling and results rendering
        grouped = bool(search_actions.get('grouped', True))
        if grouped:
            # Run grouped search via controller and render compact patent cards
            ok, msg, df = self.controller.search_patents_grouped(active_query)
            if ok and df is not None and not df.empty:
                self.ui.semantic_search_tab.render_grouped_header()
                for _, row in df.iterrows():
                    uri = row.get('uri') if isinstance(row, dict) else row['uri']
                    best_distance = float(row['best_distance']) if 'best_distance' in row else float(row.get('best_distance', 0))
                    hit_count = int(row['hit_count']) if 'hit_count' in row else int(row.get('hit_count', 0))
                    comps = row['top_components'] if 'top_components' in row else row.get('top_components', [])
                    # Normalize to a DataFrame; handle list of JSON strings or list of dicts
                    try:
                        if isinstance(comps, list) and len(comps) > 0:
                            first = comps[0]
                            # Case 1: JSON strings -> parse
                            if isinstance(first, str):
                                import json as _json
                                parsed = []
                                for _s in comps:
                                    try:
                                        parsed.append(_json.loads(_s))
                                    except Exception:
                                        continue
                                comps = parsed
                            # Case 2: BigQuery Row objects or other mapping-like entries
                            elif not isinstance(first, dict):
                                converted = []
                                for it in comps:
                                    try:
                                        converted.append(dict(it))
                                    except Exception:
                                        # As a fallback, use repr to avoid raw string blobs
                                        continue
                                if converted:
                                    comps = converted
                        top_df = pd.DataFrame(comps) if isinstance(comps, (list, tuple)) else None
                    except Exception:
                        top_df = None

                    def _make_loader(u=uri):
                        def _cb():
                            ok2, _msg2, details = self.controller.get_patent_components(active_query, u)
                            return details if ok2 else None
                        return _cb

                    def _make_signer(u=uri):
                        def _sign():
                            ok3, msg3, signed = self.controller.get_signed_patent_url(u)
                            return ok3, msg3, signed
                        return _sign

                    self.ui.semantic_search_tab.render_grouped_patent_card(
                        uri=uri,
                        best_distance=best_distance,
                        hit_count=hit_count,
                        top_components_df=top_df,
                        load_details=_make_loader(uri),
                        open_patent_cb=_make_signer(uri)
                    )
            else:
                # Fall back to info message
                self.ui.semantic_search_tab.render_grouped_header()
                try:
                    import streamlit as st
                    st.info(msg or "No patents found.")
                except Exception:
                    pass
        else:
            # Flat results using existing formatted DataFrame
            if active_query == query:
                # Use pre-fetched data when query hasn't changed
                self.ui.semantic_search_tab.render_search_results(
                    results_df=data.get('display_df'),
                    message=data.get('message', ''),
                    success=data.get('success', False),
                )
            else:
                # Fetch fresh flat results for the new query immediately
                try:
                    request = SearchRequest(query=active_query)
                    response = self.controller.search_patents(request)
                    if response.success and response.results:
                        display_df = self.controller.format_search_results_for_display(response)
                        self.ui.semantic_search_tab.render_search_results(
                            results_df=display_df,
                            message=response.message,
                            success=True,
                        )
                    else:
                        self.ui.semantic_search_tab.render_search_results(
                            results_df=None,
                            message=response.message,
                            success=response.success,
                        )
                except Exception as e:
                    self.ui.semantic_search_tab.render_search_results(
                        results_df=None,
                        message=f"Search error: {str(e)}",
                        success=False,
                    )

        # Handle new search
        if search_actions['search_clicked'] and search_actions['query']:
            if search_actions['query'] != query:  # New query
                # Trigger search; Streamlit rerun handled by the state adapter in production
                self.state.trigger_search(search_actions['query'])
    
    def run_data_tab(self):
        """Handle data visualization tab with progressive loading (section-by-section)"""
        # Check connection first for fast feedback
        status = self.controller.get_connection_status()
        if not status.gcp_connected:
            self.ui.render_data_tab_disconnected(status.gcp_message)
            return

        # Prepare progressive placeholders for sections
        sections = self.ui.render_data_tab_connected_progressive()

        # Fetch and render each section sequentially so users see results progressively
        # 1) Portfolio analysis
        try:
            p_success, p_msg, p_chart = self.ui.run_with_spinner(
                sections['portfolio_section'],
                "Loading strategic portfolio analysis...",
                lambda: self.controller.get_formatted_portfolio_chart_data()
            )
            p_payload = {'success': p_success, 'message': p_msg, 'data': p_chart}
            self.ui.render_portfolio_section(sections['portfolio_section'], p_payload)
        except Exception as e:
            self.ui.render_section_error(sections['portfolio_section'], f"Portfolio section error: {str(e)}")

        # 2) Distribution analysis
        try:
            d_success, d_msg, d_chart = self.ui.run_with_spinner(
                sections['distribution_section'],
                "Loading component distribution analysis...",
                lambda: self.controller.get_formatted_distribution_chart_data()
            )
            d_payload = {'success': d_success, 'message': d_msg, 'data': d_chart}
            self.ui.render_distribution_section(sections['distribution_section'], d_payload)
        except Exception as e:
            self.ui.render_section_error(sections['distribution_section'], f"Distribution section error: {str(e)}")

        # 3) Outlier detection
        try:
            o_success, o_msg, o_df = self.ui.run_with_spinner(
                sections['outlier_section'],
                "Performing outlier detection analysis...",
                lambda: self.controller.get_formatted_component_outliers()
            )
            o_payload = {'success': o_success, 'message': o_msg, 'data': o_df}
            self.ui.render_outlier_section(sections['outlier_section'], o_payload)
        except Exception as e:
            self.ui.render_section_error(sections['outlier_section'], f"Outlier section error: {str(e)}")
    
    def _render_data_tab_ui(self, data: dict):
        """Render data tab UI based on business data"""
        if not data.get('connected', False):
            # Delegate disconnected rendering to UI layer
            self.ui.render_data_tab_disconnected(data.get('message', 'BigQuery connection required'))
        else:
            # Delegate connected rendering to UI layer (handles layout and spinners)
            self.ui.render_data_tab_connected(
                portfolio=data.get('portfolio', {}),
                distribution=data.get('distribution', {}),
                outliers=data.get('outliers', {})
            )

    def _get_search_results(self, query: str) -> dict:
        """Get search results and format for UI (business logic only)"""
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

