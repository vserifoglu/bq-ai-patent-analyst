import streamlit as st

from components.header import render_header
from core.app_controller import AppController
from core.dashboard import DashboardEngine
from core.state_manager import StreamlitStateManager


def main():
    """Main application entry point"""
    # Initialize components with configuration
    controller = AppController()  # Uses config from environment
    state_manager = StreamlitStateManager()
    engine = DashboardEngine(controller, state_manager)
    
    # Render app header
    render_header()
    
    # Page title
    st.markdown("# 🔬 AI Patent Analyst")
    st.markdown("*From Unstructured PDFs to Queryable Knowledge Graph*")
    
    # Two-tab layout (Visualization first)
    tab1, tab2 = st.tabs(["📊 Data Analysis", "🔎 Semantic Search"])

    with tab1:
        # Engine handles data analysis tab first
        engine.run_data_tab()

    with tab2:
        # Engine orchestrates home & search as second tab
        engine.run()


if __name__ == "__main__":
    main()
