import streamlit as st
import pandas as pd


class DataVisualizationTabUI:
    """Dashboard UI class for data visualization tab"""

    def render_roi_section(self):
        """Render Business Impact & ROI metrics section above charts"""
        st.header("Business Impact & ROI")
        st.markdown(
            """
            The insights on this page are derived from an automated AI pipeline that transforms raw PDFs into a queryable intelligence asset. This approach delivers a transformative and quantifiable return on investment compared to traditional manual analysis.
            """
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                label="Manual Cost Avoided",
                value="$90,000",
                delta="Assumes 600+ expert hours @ ~$150/hr",
                delta_color="off",
            )

        with col2:
            st.metric(
                label="Immediate Project ROI",
                value="≈4,500×",
                delta="=$90k savings ÷ ~$20 pipeline run",
                delta_color="off",
            )

        with col3:
            st.metric(
                label="Time-to-Insight Reduction",
        value="≈99.9%",
        delta="605 hours → 15 minutes",
                delta_color="off",
            )

    # (Assumptions caption removed per request)

    def render_strategic_insights_header(self):
        """Display strategic insights section header"""
        st.markdown("#### 🎯 Strategic Insights from the Patent Corpus")
        st.markdown("""
            The visualizations below provide a high-level overview of the 
            entire 403-patent dataset. 
            These strategic insights are only possible because BigQuery AI 
            was used to transform the raw, unstructured PDFs into a structured 
            and queryable knowledge graph.
        """)
    
    def render_component_analysis_header(self):
        """Display component analysis section header"""
        st.markdown("#### 📈 Component Distribution Analysis")
    
    def render_portfolio_chart(self, chart_figure=None, success_message: str = None, loading: bool = False):
        """Display portfolio analysis bubble chart with loading state"""
        if loading:
            with st.spinner("Loading portfolio analysis..."):
                st.empty()  # Placeholder while loading
        elif chart_figure:
            st.plotly_chart(chart_figure, use_container_width=True)
            if success_message:
                st.success(f"✅ {success_message}")
        else:
            st.error("❌ Chart generation failed")
    
    def render_distribution_chart(self, chart_figure=None, success_message: str = None, loading: bool = False):
        """Display component distribution histogram with loading state"""
        if loading:
            with st.spinner("Loading component distribution..."):
                st.empty()  # Placeholder while loading
        elif chart_figure:
            st.plotly_chart(chart_figure, use_container_width=True)
            if success_message:
                st.success(f"✅ {success_message}")
        else:
            st.error("❌ Chart generation failed")
    
    def render_outlier_table(self, outliers_df: pd.DataFrame = None, message: str = "", 
                           has_outliers: bool = False, loading: bool = False):
        """Display outlier detection results with loading state"""
        st.markdown("**Component Count Outlier Detection**")
        
        if loading:
            with st.spinner("Detecting outliers..."):
                st.empty()  # Placeholder while loading
        elif has_outliers and outliers_df is not None and not outliers_df.empty:
            st.warning(f"⚠️ {message}")
            col_cfg = None
            try:
                if 'Open' in outliers_df.columns:
                    col_cfg = {
                        'Open': st.column_config.LinkColumn(
                            'Open',
                            help='Open the PDF in a new tab',
                            display_text='open patent ↗'
                        )
                    }
            except Exception:
                col_cfg = None
            st.dataframe(
                outliers_df,
                use_container_width=True,
                hide_index=True,
                column_config=col_cfg
            )
        else:
            st.success(f"✅ {message}")
    
    def render_portfolio_explanation(self):
        """Display portfolio analysis explanation"""
        st.markdown("""
            **Strategic Portfolio Analysis**
            
            This bubble chart reveals the strategic landscape of the patent portfolio:
            
            - **X-axis:** Average component complexity per patent
            - **Y-axis:** Total number of patents in each category  
            - **Bubble size:** Total components across all patents in category
            
            **Key Insights:**
            - Large bubbles = Categories with many total components
            - Right side = More complex individual patents
            - Top side = More patents filed in that category
        """)
    
    def render_distribution_explanation(self):
        """Display distribution analysis explanation"""
        st.markdown("""
            **Component Distribution Analysis**
            
            This histogram shows how components are distributed across patents:
            
            - **X-axis:** Number of components per patent
            - **Y-axis:** Number of patents with that component count
            
            **What this reveals:**
            - Most common patent complexity levels
            - Whether patents tend to be simple or complex
            - Outliers with unusually high/low component counts
        """)
    
    def render_loading_spinner(self, message: str):
        """Display loading spinner"""
        return st.spinner(message)

    def render_connection_warning(self, gcp_message: str):
        """Show connection warning when BigQuery is not connected"""
        st.warning("🔗 Data visualization requires BigQuery connection")
        if gcp_message:
            st.info(gcp_message)
        st.info("💡 Configure your environment to see real visualizations.")

    def render_visualization_placeholder(self):
        """Preview layout placeholders when disconnected"""
        st.markdown("#### Preview Layout")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Left Column:** Component Distribution Histogram")
            st.container(height=200, border=True)
        with col2:
            st.markdown("**Right Column:** Strategic Portfolio Analysis")
            st.container(height=200, border=True)
