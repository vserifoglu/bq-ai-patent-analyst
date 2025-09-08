"""Main application launcher - ultra simple"""
import streamlit as st

from components.header import render_header
from core.app_controller import AppController
from core.dashboard import DashboardEngine
from core.state_manager import StateManager


def main():
    """Main application entry point"""
    # Initialize components with configuration
    controller = AppController()  # Uses config from environment
    state_manager = StateManager()  # Now returns StreamlitStateAdapter
    engine = DashboardEngine(controller, state_manager)
    
    # Render app header
    render_header()
    
    # Page title
    st.markdown("# 🔬 AI Patent Analyst")
    st.markdown("*From Unstructured PDFs to Queryable Knowledge Graph*")
    
    # Two-tab layout
    tab1, tab2 = st.tabs(["🏠 Home & Search", "📊 Data Analysis"])
    
    with tab1:
        # Engine orchestrates everything
        engine.run()
    
    with tab2:
        # Engine handles data analysis tab
        engine.run_data_tab()


if __name__ == "__main__":
    main()
