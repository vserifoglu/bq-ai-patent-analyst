import streamlit as st
from typing import Optional, Callable
from core.interfaces.state_interface import StateInterface


class StreamlitStateAdapter(StateInterface):
    """Streamlit-specific implementation of state interface"""
    
    def __init__(self, rerun_callback: Optional[Callable] = None):
        """
        Initialize with optional rerun callback for testing
        If no callback provided, uses st.rerun()
        """
        self._rerun_callback = rerun_callback or st.rerun
        self._initialize_state()
    
    def _initialize_state(self):
        """Initialize session state variables if they don't exist"""
        if 'search_triggered' not in st.session_state:
            st.session_state.search_triggered = False
        if 'search_query' not in st.session_state:
            st.session_state.search_query = ""
        if 'search_input' not in st.session_state:
            st.session_state.search_input = ""
    
    def is_search_triggered(self) -> bool:
        """Check if search mode is active"""
        return st.session_state.get('search_triggered', False)
    
    def get_search_query(self) -> str:
        """Get current search query"""
        return st.session_state.get('search_query', "")
    
    def trigger_search(self, query: str) -> None:
        """Trigger search mode with given query"""
        st.session_state.search_query = query
        st.session_state.search_triggered = True
        self._rerun_callback()
    
    def reset_search(self) -> None:
        """Reset search mode to overview"""
        st.session_state.search_triggered = False
        st.session_state.search_query = ""
        self._rerun_callback()
    
    def get_search_input(self) -> Optional[str]:
        """Get search input from session state"""
        return st.session_state.get('search_input', '')
    
    def is_overview_mode(self) -> bool:
        """Check if in overview mode (not searching)"""
        return not self.is_search_triggered()
