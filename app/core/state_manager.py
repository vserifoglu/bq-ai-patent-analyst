"""Session state management abstraction for Streamlit"""
import streamlit as st
from typing import Optional


class StateManager:
    """Manages Streamlit session state with clean abstraction"""
    
    def __init__(self):
        """Initialize session state variables"""
        self._initialize_state()
    
    def _initialize_state(self):
        """Initialize session state variables if they don't exist"""
        if 'search_triggered' not in st.session_state:
            st.session_state.search_triggered = False
        if 'search_query' not in st.session_state:
            st.session_state.search_query = ""
    
    def is_search_triggered(self) -> bool:
        """Check if search mode is active"""
        return st.session_state.get('search_triggered', False)
    
    def get_search_query(self) -> str:
        """Get current search query"""
        return st.session_state.get('search_query', "")
    
    def trigger_search(self, query: str):
        """Trigger search mode with given query"""
        st.session_state.search_query = query
        st.session_state.search_triggered = True
        st.rerun()
    
    def reset_search(self):
        """Reset search mode to overview"""
        st.session_state.search_triggered = False
        st.session_state.search_query = ""
        st.rerun()
    
    def get_search_input(self) -> Optional[str]:
        """Get search input from session state"""
        return st.session_state.get('search_input', '')
    
    def is_overview_mode(self) -> bool:
        """Check if in overview mode (not searching)"""
        return not self.is_search_triggered()
