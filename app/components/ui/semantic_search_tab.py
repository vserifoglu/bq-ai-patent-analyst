import streamlit as st
import pandas as pd


class SemanticSearchTabUI:
    """UI class for semantic search tab"""
    
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

            # View toggle
            grouped_view = st.toggle("Group results by patent", value=True, help="Show a patent summary with top component hits")
        
        return {
            'query': search_input.strip() if search_input else "",
            'search_clicked': search_clicked,
            'grouped': grouped_view
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

    # ---------------- Phase A: Grouped results UI helpers ----------------
    def render_grouped_header(self):
        st.markdown("### 🧩 Grouped by patent")

    def render_grouped_patent_card(self, uri: str, best_distance: float, hit_count: int, top_components_df, load_details=None, open_patent_cb=None):
        exp = st.expander(f"{uri}", expanded=False)
        with exp:
            # Prefetch signed URL and show a blue clickable link above the metrics
            if callable(open_patent_cb):
                @st.cache_data(show_spinner=False, ttl=600)
                def _cached_signed_url(key: str):
                    return open_patent_cb()

                try:
                    ok, msg, signed_url = _cached_signed_url(str(uri))
                    if ok and signed_url:
                        st.markdown(f"[open patent ↗]({signed_url})")
                    else:
                        st.caption(msg or "Link not available for this URI.")
                except Exception:
                    st.caption("Link not available.")
            col1, col2 = st.columns([1,1])
            with col1:
                st.metric("Best distance", f"{best_distance:.3f}")
            with col2:
                st.metric("Matches", int(hit_count))
            # Show top components immediately
            if top_components_df is not None:
                try:
                    import pandas as _pd  # local import to avoid global hard dep
                    if isinstance(top_components_df, list):
                        # If list contains JSON strings, parse them first
                        if len(top_components_df) > 0 and isinstance(top_components_df[0], str):
                            import json as _json
                            parsed = []
                            for _s in top_components_df:
                                try:
                                    parsed.append(_json.loads(_s))
                                except Exception:
                                    continue
                            _df = _pd.DataFrame(parsed)
                        else:
                            _df = _pd.DataFrame(top_components_df)
                    else:
                        _df = top_components_df
                    if _df is not None and not _df.empty:
                        st.markdown("Top components")
                        st.dataframe(_df, use_container_width=True, hide_index=True)
                except Exception:
                    pass
            # Load and show full components list without a button
            if callable(load_details):
                try:
                    details = load_details()
                    import pandas as _pd
                    if isinstance(details, list):
                        details_df = _pd.DataFrame(details)
                    else:
                        details_df = details
                    if details_df is not None and not details_df.empty:
                        st.markdown("All components")
                        st.dataframe(details_df, use_container_width=True, hide_index=True)
                except Exception:
                    pass
    
    def render_loading_spinner(self, query: str):
        """Display loading spinner for search"""
        return st.spinner(f"Searching for: '{query}'...")
