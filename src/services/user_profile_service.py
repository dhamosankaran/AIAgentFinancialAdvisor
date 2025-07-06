"""
User Profile Service for managing user profiles and preferences
"""

import json
from typing import Dict, List, Optional
from datetime import datetime
import logging
from pathlib import Path

from src.models.user_profile import UserProfile, InvestmentPreference

logger = logging.getLogger(__name__)

class UserProfileService:
    """Service for managing user profiles"""
    
    def __init__(self):
        self.data_dir = Path("data")
        self.profile_file = self.data_dir / "user_profile.json"
        self._ensure_data_dir()
    
    def _ensure_data_dir(self):
        """Ensure data directory exists"""
        self.data_dir.mkdir(exist_ok=True)
    
    def save_profile(self, profile: UserProfile) -> bool:
        """Save user profile to file"""
        try:
            # Update timestamp
            profile.updated_at = datetime.now()
            
            # Convert to dict and save
            profile_dict = profile.model_dump()
            with open(self.profile_file, 'w') as f:
                json.dump(profile_dict, f, indent=2, default=str)
            
            return True
        except Exception as e:
            logger.error(f"Error saving user profile: {str(e)}")
            return False
    
    def load_profile(self) -> Optional[UserProfile]:
        """Load user profile from file"""
        try:
            if not self.profile_file.exists():
                return None
            
            with open(self.profile_file, 'r') as f:
                profile_dict = json.load(f)
            
            return UserProfile(**profile_dict)
        except Exception as e:
            logger.error(f"Error loading user profile: {str(e)}")
            return None
    
    def update_preferences(self, preferences: List[InvestmentPreference]) -> bool:
        """Update user investment preferences"""
        try:
            profile = self.load_profile()
            if not profile:
                return False
            
            profile.preferences = preferences
            profile.updated_at = datetime.now()
            
            return self.save_profile(profile)
        except Exception as e:
            logger.error(f"Error updating preferences: {str(e)}")
            return False
    
    def get_portfolio_summary(self) -> Dict:
        """Get summary of user's investment portfolio"""
        try:
            profile = self.load_profile()
            if not profile:
                return {"error": "No user profile found"}
            
            # Calculate total allocation
            total_allocation = sum(p.allocation_percentage for p in profile.preferences if p.is_active)
            
            # Group by asset type
            asset_groups = {}
            for pref in profile.preferences:
                if pref.is_active:
                    if pref.asset_type not in asset_groups:
                        asset_groups[pref.asset_type] = 0
                    asset_groups[pref.asset_type] += pref.allocation_percentage
            
            return {
                "user_id": profile.user_id,
                "name": profile.name,
                "risk_tolerance": profile.risk_tolerance,
                "investment_goal": profile.investment_goal,
                "investment_horizon": profile.investment_horizon,
                "total_allocation": total_allocation,
                "asset_allocation": asset_groups,
                "last_updated": profile.updated_at.isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting portfolio summary: {str(e)}")
            return {"error": str(e)}
    
    def create_default_profile(self, user_id: str, name: str, age: int, income: float) -> UserProfile:
        """Create a default user profile with balanced allocation"""
        default_preferences = [
            InvestmentPreference(asset_type="stocks", allocation_percentage=50, risk_tolerance="moderate"),
            InvestmentPreference(asset_type="bonds", allocation_percentage=20, risk_tolerance="conservative"),
            InvestmentPreference(asset_type="cash", allocation_percentage=5, risk_tolerance="conservative"),
            InvestmentPreference(asset_type="real estate", allocation_percentage=10, risk_tolerance="moderate"),
            InvestmentPreference(asset_type="commodities", allocation_percentage=5, risk_tolerance="moderate"),
            InvestmentPreference(asset_type="cryptocurrency", allocation_percentage=3, risk_tolerance="aggressive"),
            InvestmentPreference(asset_type="etfs", allocation_percentage=5, risk_tolerance="moderate"),
            InvestmentPreference(asset_type="reits", allocation_percentage=2, risk_tolerance="moderate")
        ]
        profile = UserProfile(
            user_id=user_id,
            name=name,
            age=age,
            income=income,
            risk_tolerance="moderate",
            investment_goal="balanced_growth",
            investment_horizon="long-term",
            preferences=default_preferences
        )
        self.save_profile(profile)
        return profile 