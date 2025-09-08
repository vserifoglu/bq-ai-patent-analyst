"""State manager convenience exports.

Provide explicit names for clarity:
- StreamlitStateManager: production adapter using st.session_state
- PureStateManager: framework-independent in-memory manager (for tests)
"""
from core.state.streamlit_state_adapter import StreamlitStateAdapter as StreamlitStateManager
from core.state.state_manager import PureStateManager

# Backward-compatible default
StateManager = StreamlitStateManager
