from dataclasses import dataclass
from typing import Optional
from core.interfaces.state_interface import StateInterface


@dataclass
class AppState:
    """Application state data structure"""
    search_triggered: bool = False
    search_query: str = ""
    search_input: str = ""


class PureStateManager(StateInterface):
    """Framework-independent in-memory state manager"""
    
    def __init__(self, initial_state: Optional[AppState] = None):
        """Initialize with optional initial state for testing"""
        self.state = initial_state or AppState()
    
    def is_search_triggered(self) -> bool:
        """Check if search mode is active"""
        return self.state.search_triggered
    
    def get_search_query(self) -> str:
        """Get current search query"""
        return self.state.search_query
    
    def trigger_search(self, query: str) -> None:
        """Trigger search mode with given query"""
        self.state.search_query = query
        self.state.search_triggered = True
    
    def reset_search(self) -> None:
        """Reset search mode to overview"""
        self.state.search_triggered = False
        self.state.search_query = ""
    
    def get_search_input(self) -> Optional[str]:
        """Get search input from state"""
        return self.state.search_input
    
    def is_overview_mode(self) -> bool:
        """Check if in overview mode (not searching)"""
        return not self.is_search_triggered()
    
    def set_search_input(self, input_value: str) -> None:
        """Set search input value (helper method)"""
        self.state.search_input = input_value

# Backward-compatible alias (deprecated): will be removed after migration
StateManager = PureStateManager
