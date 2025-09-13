import streamlit as st
import pandas as pd


class SemanticSearchTabUI:
    """UI class for semantic search tab"""
    
    def render_project_narrative(self):
        """Minimal narrative (intentionally left blank; search box provides context)."""
        pass
    
    def render_search_box(self, current_query: str = "") -> dict:
        """Render search input and return user actions"""
        # Center the search section header and search components
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            # Combined, concise intro
            st.header("🔎 Semantic Component Search")
            st.markdown(
                """
                Enter a technical function below to search the knowledge graph. The AI-powered search will find the most functionally similar components and their parent patents, regardless of keywords.
                """
            )

            # Quick examples
            st.subheader("Quick Examples")
            ex_query = None
            ex_cols = st.columns(4)
            examples = [
                ("Encryption Algorithm", "Encryption Algorithm"),
                ("Data Compression", "Data Compression"),
                ("Thermal Management", "Thermal management system"),
                ("Battery Safety", "Battery protection and safety")
            ]
            for i, (label, val) in enumerate(examples):
                with ex_cols[i]:
                    if st.button(label, key=f"ex_btn_{i}"):
                        ex_query = val
                        # Write the example into the search box immediately
                        try:
                            st.session_state["search_input"] = val
                        except Exception:
                            pass

            st.markdown("")  # spacing

            # Initialize the text input from current_query if first render
            if "search_input" not in st.session_state:
                st.session_state["search_input"] = current_query or ""

            # Search input field
            search_input = st.text_input(
                "What technical function are you looking for?",
                placeholder="e.g., 'precise fluid delivery mechanism' or 'user authentication method'",
                key="search_input",
                help="Enter a functional description, e.g., 'a mechanism for precise fluid delivery' or 'a method for authenticating a user'."
            )

            # Controls
            search_clicked = st.button("🔍 Search Patents", type="primary", use_container_width=True)
            grouped_mode = st.checkbox(
                "Group results by patent",
                value=True,
                help="Recommended for readability. Uncheck to see a flat, ungrouped list of all matching components."
            )

            # Resolve effective query and mode
            effective_query = ex_query if ex_query else search_input
            grouped_view = bool(grouped_mode)
        
        return {
            'query': effective_query.strip() if effective_query else "",
            'search_clicked': bool(search_clicked or ex_query),
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
