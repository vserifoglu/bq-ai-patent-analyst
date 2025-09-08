"""Pure UI components for the Semantic Search tab - search and overview"""
import streamlit as st
import pandas as pd


class SemanticSearchTabUI:
    """Pure UI class for semantic search tab - no business logic"""
    
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
    
    def render_search_box(self, current_query: str = "") -> dict:
        """Render search input and return user actions"""
        # Center the search section header and search components
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            # Centered search header and description
            st.markdown("### 🔍 Search Patent Knowledge Graph")
            st.markdown("""
            Enter your technical question below. Our AI will search through the patent knowledge graph 
            to find relevant components and technical details.
            """)
            
            st.markdown("")  # Add some spacing
            
            # Search input field
            search_input = st.text_input(
                "What technical components are you looking for?",
                value=current_query,
                placeholder="e.g., 'wireless communication modules' or 'battery management systems'",
                key="search_input",
                help="Ask questions about technical components, materials, or patent details"
            )
            
            # Search button
            search_clicked = st.button("🔍 Search Patents", type="primary", use_container_width=True)
        
        return {
            'query': search_input.strip() if search_input else "",
            'search_clicked': search_clicked
        }
    
    def render_search_results(self, results_df: pd.DataFrame, message: str, success: bool):
        """Display search results table"""
        st.markdown("### 📊 Search Results")
        
        if success:
            if results_df is not None and not results_df.empty:
                st.success(message)
                
                st.dataframe(
                    results_df,
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
                st.info(message)
        else:
            if "not connected" in message.lower():
                st.warning(f"🔗 {message}")
                st.info("💡 Configure your .env file to connect to real data.")
            else:
                st.error(f"❌ {message}")
    
    def render_loading_spinner(self, query: str):
        """Display loading spinner for search"""
        return st.spinner(f"Searching for: '{query}'...")
