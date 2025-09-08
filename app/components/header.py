"""Header component with title and navigation"""
import streamlit as st
from config.settings import APP_TITLE

def render_header():
    """Render the application header"""
    st.set_page_config(
        page_title=APP_TITLE,
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Custom CSS for styling
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 2rem;
    }
    .main-title {
        font-size: 3rem;
        font-weight: 700;
        color: #1f1f1f;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

def render_page_title(title: str, subtitle: str = None):
    """Render a page title with optional subtitle"""
    st.markdown(f'<h1 class="main-title">{title}</h1>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<p class="subtitle">{subtitle}</p>', unsafe_allow_html=True)
