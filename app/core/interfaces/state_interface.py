"""State management interface - framework independent"""
from abc import ABC, abstractmethod
from typing import Optional


class StateInterface(ABC):
    """Abstract interface for application state management"""
    
    @abstractmethod
    def is_search_triggered(self) -> bool:
        """Check if search mode is active"""
        pass
    
    @abstractmethod
    def get_search_query(self) -> str:
        """Get current search query"""
        pass
    
    @abstractmethod
    def trigger_search(self, query: str) -> None:
        """Trigger search mode with given query"""
        pass
    
    @abstractmethod
    def reset_search(self) -> None:
        """Reset search mode to overview"""
        pass
    
    @abstractmethod
    def get_search_input(self) -> Optional[str]:
        """Get search input from state"""
        pass
    
    @abstractmethod
    def is_overview_mode(self) -> bool:
        """Check if in overview mode (not searching)"""
        pass
