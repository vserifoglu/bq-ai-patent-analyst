"""Pure UI components for the dashboard - no business logic"""
import streamlit as st
import pandas as pd
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from components.header import render_header
from core.app_controller import AppController
from core.models import SearchRequest


class DashboardUI:
    """Pure UI class for dashboard rendering"""
    
    def __init__(self, controller: AppController):
        self.controller = controller
    
    def render_connection_status(self):
        """Display GCP connection status in sidebar"""
        with st.sidebar:
            st.markdown("### 🔗 Connection Status")
            
            # Get status from controller
            status = self.controller.get_connection_status()
            
            if status.env_valid:
                st.success("✅ Environment configured")
            else:
                st.error(f"❌ Environment: {status.env_message}")
                return
            
            if status.gcp_connected:
                st.success("✅ BigQuery connected")
            else:
                st.warning(f"⚠️ BigQuery: {status.gcp_message}")
            
            # Show stats
            stats = self.controller.get_app_stats()
            if stats:
                st.metric("Patents", stats.patent_count)
                st.metric("Components", stats.component_count)
                st.caption(f"Status: {stats.connection_status}")
            else:
                st.error("Stats error")
    
    def render_project_narrative(self):
        """Display project description and business impact"""
        st.markdown("""
        ## The Challenge: Analyzing Unstructured Patent Data
        
        Patent analysis traditionally requires hundreds of hours of expensive expert analysis from patent lawyers 
        or R&D engineers. This project solves the critical challenge of analyzing unstructured patent PDFs by 
        building an end-to-end pipeline that transforms them into a structured, queryable Knowledge Graph.
        
        **Business Impact:**
        - **Time Savings:** Reduce research time from hours to minutes
        - **Cost Efficiency:** Automate tasks requiring expert analysis
        - **Deep Insights:** Discover hidden technical patterns across patents
        - **Scalable Analysis:** Process hundreds of patents automatically
        """)
    
    def render_search_input(self):
        """Display search input field"""
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("### 🔍 Patent Component Search")
            
            search_query = st.text_input(
                "Enter technology or component description:",
                placeholder="e.g., encryption mechanism, data compression algorithm",
                help="Describe the technology or component you're looking for",
                key="search_input",
                on_change=self._handle_search_input_change
            )
            
            if st.button("🔍 Search Patents", type="primary", use_container_width=True, key="search_btn"):
                if search_query:
                    self._trigger_search(search_query)
    
    def render_back_button(self):
        """Display back to overview button"""
        if st.button("📖 Back to Project Overview", key="back_to_overview"):
            st.session_state.search_triggered = False
            st.session_state.search_query = ""
            st.rerun()
    
    def render_search_results(self, query: str):
        """Display search results for given query"""
        st.markdown("### 📊 Search Results")
        
        with st.spinner(f"Searching for: '{query}'..."):
            # Get results from controller
            request = SearchRequest(query=query)
            response = self.controller.search_patents(request)
            
            if response.success:
                if response.results:
                    st.success(response.message)
                    
                    # Convert to DataFrame for display
                    data = []
                    for result in response.results:
                        data.append({
                            "Patent URI": result.patent_uri,
                            "Component": result.component,
                            "Function": result.function,
                            "Similarity": result.similarity
                        })
                    
                    display_df = pd.DataFrame(data)
                    
                    st.dataframe(
                        display_df,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Similarity": st.column_config.ProgressColumn(
                                "Similarity",
                                help="Semantic similarity score",
                                min_value=0,
                                max_value=100,
                                format="%d%%",
                            ),
                        }
                    )
                    
                    st.success("🎯 Results from your BigQuery knowledge graph")
                else:
                    st.info(response.message)
            else:
                if "not connected" in response.message.lower():
                    st.warning(f"🔗 {response.message}")
                    st.info("💡 Configure your .env file to connect to real data.")
                else:
                    st.error(f"❌ {response.message}")
    
    def render_data_analysis_tab(self):
        """Display real data analysis visualizations with explanations"""
        # Check connection first
        status = self.controller.get_connection_status()
        
        if not status.gcp_connected:
            st.warning(f"🔗 BigQuery not connected: {status.gcp_message}")
            st.info("💡 Configure your .env file to see real visualizations.")
            self._render_visualization_placeholder()
            return
        
        # Strategic Portfolio Analysis (First)
        st.markdown("#### 🎯 Strategic Insights from the Patent Corpus")
        st.markdown("""
        The visualizations below provide a high-level overview of the entire 403-patent dataset. These strategic insights are only possible because BigQuery AI was used to transform the raw, unstructured PDFs into a structured and queryable knowledge graph.
        """)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            self._render_portfolio_analysis()
        
        with col2:
            self._render_portfolio_analysis_explanation()
        
        # Add separator
        st.markdown("---")
        
        # Component Distribution Analysis (Second)
        st.markdown("#### 📈 Component Distribution Analysis")
        col3, col4 = st.columns([2, 1])
        
        with col3:
            self._render_component_distribution()
        
        with col4:
            self._render_component_distribution_explanation()
        
        # Add separator
        st.markdown("---")
        
        # Component Count Outlier Detection (Third)
        self._render_outlier_analysis()
    
    def _render_component_distribution(self):
        """Render component distribution histogram"""
        with st.spinner("Loading component distribution..."):
            success, message, df_distribution = self.controller.get_component_distribution()
            
            if success and df_distribution is not None:
                try:
                    import plotly.express as px
                    
                    # Get outliers for marking on histogram
                    outlier_success, _, df_outliers = self.controller.get_component_outliers()
                    
                    # Create histogram
                    fig = px.histogram(
                        df_distribution,
                        x="num_components",
                        title="Distribution of Component Counts",
                        labels={"num_components": "Number of Components per Patent"}
                    )
                    
                    # Add outlier lines if available
                    if outlier_success and df_outliers is not None and not df_outliers.empty:
                        for _, row in df_outliers.iterrows():
                            fig.add_vline(
                                x=row['num_components'],
                                line_width=2,
                                line_dash="dash",
                                line_color="red"
                            )
                    
                    fig.update_layout(
                        xaxis_title="Number of Components",
                        yaxis_title="Number of Patents",
                        font=dict(family="Arial, sans-serif", size=12),
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    st.success(f"✅ {message}")
                    
                except ImportError:
                    st.error("❌ Plotly not available for visualization")
                except Exception as e:
                    st.error(f"❌ Visualization error: {str(e)}")
            else:
                st.error(f"❌ {message}")
    
    def _render_portfolio_analysis(self):
        """Render strategic portfolio analysis bubble chart"""
        with st.spinner("Loading portfolio analysis..."):
            success, message, df_portfolio = self.controller.get_portfolio_analysis()
            
            if success and df_portfolio is not None:
                try:
                    import plotly.express as px
                    
                    # Create bubble chart
                    fig = px.scatter(
                        df_portfolio,
                        x="innovation_breadth",
                        y="average_connection_density",
                        size="total_patents",
                        color="applican",
                        hover_name="applican",
                        size_max=60,
                        title="Strategic Patent Portfolio Analysis",
                        labels={
                            "innovation_breadth": "Innovation Breadth (Number of Domains)",
                            "average_connection_density": "Average Connection Density"
                        }
                    )
                    
                    fig.update_layout(
                        showlegend=False,
                        xaxis_title="Innovation Breadth ➡️",
                        yaxis_title="Architectural Complexity ⬆️",
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    st.success(f"✅ {message}")
                    
                except ImportError:
                    st.error("❌ Plotly not available for visualization")
                except Exception as e:
                    st.error(f"❌ Visualization error: {str(e)}")
            else:
                st.error(f"❌ {message}")
    
    def _render_component_distribution_explanation(self):
        """Render explanation for component distribution chart"""
        st.markdown("**📋 Analysis Insights**")
        
        st.markdown("""
        This chart reveals that **most patents in our dataset are of normal complexity**, typically having between 2 and 15 components. The long tail to the right, marked by the red lines, shows that patents with a high number of components are rare outliers.
        
        **Key Finding:** Our analysis confirms that these outliers are patents that contain technical diagrams. This proves that the true architectural complexity of an invention is often hidden within its visual data. 
        
        **Why This Matters:** Our multimodal pipeline is essential because it successfully unlocks this deeper layer of information, providing a much richer and more accurate understanding than a text-only analysis ever could.
        """)
    
    def _render_portfolio_analysis_explanation(self):
        """Render explanation for portfolio analysis chart"""
        st.markdown("**📋 Strategic Insights**")
        
        st.markdown("""
        This chart is a **strategic map of the patent applicants** in our dataset. Each bubble represents a single company.
        
        **📍 Chart Navigation:**
        
        • **Position Right ➡️** (Innovation Breadth): Shows companies that are more diverse, patenting across many different technology domains.
        
        • **Position Top ⬆️** (Architectural Complexity): Shows companies that build more complex inventions with a higher number of connections between components.
        
        • **Bubble Size ⚪** (Portfolio Size): Shows who is most prolific, with larger bubbles representing more total patents.
        
        **Strategic Value:** This allows us to instantly identify different innovation strategies, such as a large, diverse innovator in the top-right versus a specialized, deep-tech player in the top-left.
        """)
    
    def _render_outlier_analysis(self):
        """Render outlier detection analysis"""
        st.markdown("**Component Count Outlier Detection**")
        
        with st.spinner("Detecting outliers..."):
            success, message, df_outliers = self.controller.get_component_outliers()
            
            if success:
                if df_outliers is not None and not df_outliers.empty:
                    st.warning(f"⚠️ {message}")
                    
                    # Display outliers table
                    display_df = df_outliers.copy()
                    display_df['Patent'] = display_df['uri'].apply(lambda x: x.split('/')[-1])
                    display_df = display_df[['Patent', 'num_components']].rename(columns={
                        'Patent': 'Patent ID',
                        'num_components': 'Component Count'
                    })
                    
                    # Sort by component count from highest to lowest
                    display_df = display_df.sort_values('Component Count', ascending=False)
                    
                    st.dataframe(
                        display_df,
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.success(f"✅ {message}")
            else:
                st.error(f"❌ {message}")
    
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
    
    def render_home_tab(self):
        """Orchestrate home tab display"""
        search_triggered = st.session_state.get('search_triggered', False)
        
        if search_triggered:
            query = st.session_state.get('search_query', '')
            # Search mode: search interface at top
            self.render_search_input()
            st.markdown("---")
            self.render_search_results(query)
            st.markdown("---")
            self.render_back_button()
        else:
            # Overview mode: narrative first, then search
            self.render_project_narrative()
            st.markdown("---")
            self.render_search_input()
    
    def _handle_search_input_change(self):
        """Handle Enter key press in search input"""
        search_query = st.session_state.search_input
        if search_query and search_query.strip():
            self._trigger_search(search_query)
    
    def _trigger_search(self, query: str):
        """Trigger search and update session state"""
        st.session_state.search_query = query
        st.session_state.search_triggered = True
        st.rerun()
    
    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'search_triggered' not in st.session_state:
            st.session_state.search_triggered = False
        if 'search_query' not in st.session_state:
            st.session_state.search_query = ""
