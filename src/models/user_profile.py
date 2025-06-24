"""
User Profile Model for storing user preferences and investment choices
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class InvestmentPreference(BaseModel):
    """Investment preference for a specific asset class"""
    asset_type: str
    allocation_percentage: float = Field(ge=0, le=100)
    risk_tolerance: str = "moderate"  # conservative, moderate, aggressive
    is_active: bool = True

class UserProfile(BaseModel):
    """User profile with investment preferences"""
    user_id: str
    name: str
    age: int
    income: float
    risk_tolerance: str = "moderate"
    investment_goal: str
    investment_horizon: str  # short-term, medium-term, long-term
    preferences: List[InvestmentPreference] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    last_report: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "name": "John Doe",
                "age": 35,
                "income": 100000,
                "risk_tolerance": "moderate",
                "investment_goal": "retirement",
                "investment_horizon": "long-term",
                "preferences": [
                    {"asset_type": "stocks", "allocation_percentage": 60, "risk_tolerance": "moderate", "is_active": True},
                    {"asset_type": "bonds", "allocation_percentage": 20, "risk_tolerance": "conservative", "is_active": True},
                    {"asset_type": "cash", "allocation_percentage": 5, "risk_tolerance": "conservative", "is_active": True},
                    {"asset_type": "real estate", "allocation_percentage": 5, "risk_tolerance": "moderate", "is_active": True},
                    {"asset_type": "commodities", "allocation_percentage": 5, "risk_tolerance": "moderate", "is_active": True},
                    {"asset_type": "cryptocurrency", "allocation_percentage": 2, "risk_tolerance": "aggressive", "is_active": True},
                    {"asset_type": "etfs", "allocation_percentage": 2, "risk_tolerance": "moderate", "is_active": True},
                    {"asset_type": "reits", "allocation_percentage": 1, "risk_tolerance": "moderate", "is_active": True}
                ]
            }
        } 