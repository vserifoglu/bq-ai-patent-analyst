"""Pydantic models for data flow between controller and UI"""
from typing import List, Optional
from pydantic import BaseModel


class SearchRequest(BaseModel):
    """Search request from UI to controller"""
    query: str
    
    class Config:
        str_strip_whitespace = True


class SearchResult(BaseModel):
    """Individual search result"""
    patent_uri: str
    component: str
    function: str
    similarity: int


class SearchResponse(BaseModel):
    """Search response from controller to UI"""
    success: bool
    message: str
    results: List[SearchResult] = []
    query: str = ""
    
    @classmethod
    def from_dataframe(cls, success: bool, message: str, df=None, query: str = ""):
        """Create SearchResponse from pandas DataFrame"""
        results = []
        if df is not None and not df.empty:
            for _, row in df.iterrows():
                results.append(SearchResult(
                    patent_uri=row.get('Patent URI', ''),
                    component=row.get('Component', ''),
                    function=row.get('Function', ''),
                    similarity=row.get('Similarity', 0)
                ))
        
        return cls(
            success=success,
            message=message,
            results=results,
            query=query
        )


class ConnectionStatus(BaseModel):
    """Connection status information"""
    env_valid: bool
    env_message: str
    gcp_connected: bool
    gcp_message: str


class AppStats(BaseModel):
    """Application statistics"""
    patent_count: str
    component_count: str
    connection_status: str
