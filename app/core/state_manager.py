"""Clean state manager implementation using new architecture"""
from core.state.streamlit_state_adapter import StreamlitStateAdapter

# Export the Streamlit implementation as default StateManager
StateManager = StreamlitStateAdapter
