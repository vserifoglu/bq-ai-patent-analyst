"""Main application launcher - ultra simple"""
import streamlit as st
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.dirname(__file__))

from components.header import render_header
from core.app_controller import AppController
from core.simple_dashboard_engine import SimpleDashboardEngine
from core.state_manager import StateManager


def main():
    """Main application entry point"""
    # Initialize components
    controller = AppController()
    state_manager = StateManager()
    engine = SimpleDashboardEngine(controller, state_manager)
    
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
