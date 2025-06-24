"""
Financial Analysis Pipeline (FAP) Context Model
Manages context and state throughout the financial analysis workflow
"""
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

class FAPContext(BaseModel):
    """
    Financial Analysis Pipeline Context
    
    Maintains state and context throughout the multi-step financial analysis process.
    This is NOT the Model Context Protocol (MCP) - it's a custom workflow system
    for financial analysis.
    """
    user_profile: Dict[str, Any]
    session_id: str
    risk_assessment: Optional[Dict[str, Any]] = None
    market_analysis: Optional[Dict[str, Any]] = None
    portfolio_allocation: Optional[Dict[str, Any]] = None
    report: Optional[str] = None
    history: List[Dict[str, Any]] = [] 