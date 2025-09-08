"""Main application launcher - ultra simple"""
import streamlit as st
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.dirname(__file__))

from components.header import render_header
from core.app_controller import AppController
from pages.dashboard import DashboardUI


def main():
    """Main application entry point"""
    # Initialize controller and UI
    controller = AppController()
    dashboard = DashboardUI(controller)
    
    # Initialize session state
    dashboard.initialize_session_state()
    
    # Render app
    render_header()
    dashboard.render_connection_status()
    
    # Page title
    st.markdown("# 🔬 AI Patent Analyst")
    st.markdown("*From Unstructured PDFs to Queryable Knowledge Graph*")
    
    # Two-tab layout
    tab1, tab2 = st.tabs(["🏠 Home & Search", "📊 Data Analysis"])
    
    with tab1:
        dashboard.render_home_tab()
    
    with tab2:
        dashboard.render_data_analysis_tab()


if __name__ == "__main__":
    main()
