"""
Profile Portfolio Service for storing and retrieving profile-based portfolio allocations
"""

import json
import os
from datetime import datetime
from typing import Dict, Optional, Any, List
import logging

logger = logging.getLogger(__name__)

class ProfilePortfolioService:
    """Service for managing profile-based portfolio storage and retrieval"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.portfolio_file = os.path.join(data_dir, "profile_portfolio.json")
        self._ensure_data_directory()
    
    def _ensure_data_directory(self):
        """Ensure the data directory exists"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def save_profile_portfolio(self, 
                              user_profile: Dict[str, Any], 
                              portfolio_allocation: List[Dict[str, Any]], 
                              portfolio_summary: str) -> Dict[str, Any]:
        """
        Save profile-based portfolio allocation and summary
        
        Args:
            user_profile: User profile information
            portfolio_allocation: Portfolio allocation data
            portfolio_summary: Portfolio summary text
            
        Returns:
            Saved portfolio entry with metadata
        """
        try:
            # Create portfolio entry
            portfolio_entry = {
                "id": f"profile_portfolio_{int(datetime.now().timestamp())}",
                "timestamp": datetime.now().isoformat(),
                "user_profile": user_profile,
                "portfolio_allocation": portfolio_allocation,
                "portfolio_summary": portfolio_summary,
                "risk_profile": user_profile.get("risk_tolerance", "moderate"),
                "total_allocation": sum(item.get("allocation_percentage", 0) for item in portfolio_allocation),
                "asset_classes": len(portfolio_allocation),
                "last_updated": datetime.now().isoformat()
            }
            
            # Save to file
            with open(self.portfolio_file, 'w') as f:
                json.dump(portfolio_entry, f, indent=2)
            
            logger.info("Saved profile portfolio to local storage")
            return portfolio_entry
            
        except Exception as e:
            logger.error(f"Error saving profile portfolio: {str(e)}")
            raise
    
    def load_profile_portfolio(self) -> Optional[Dict[str, Any]]:
        """
        Load the most recent profile portfolio from file
        
        Returns:
            Profile portfolio if found, None otherwise
        """
        try:
            if not os.path.exists(self.portfolio_file):
                return None
            
            with open(self.portfolio_file, 'r') as f:
                portfolio = json.load(f)
                
            # Add loaded flag
            if portfolio:
                portfolio["loaded_from_storage"] = True
                
            return portfolio
                
        except Exception as e:
            logger.error(f"Error loading profile portfolio: {str(e)}")
            return None
    
    def update_profile_portfolio(self, 
                                user_profile: Dict[str, Any], 
                                portfolio_allocation: List[Dict[str, Any]], 
                                portfolio_summary: str) -> Dict[str, Any]:
        """
        Update existing profile portfolio or create new one
        
        Args:
            user_profile: Updated user profile information
            portfolio_allocation: Updated portfolio allocation data
            portfolio_summary: Updated portfolio summary text
            
        Returns:
            Updated portfolio entry
        """
        try:
            # Load existing portfolio
            existing_portfolio = self.load_profile_portfolio()
            
            # Create updated entry
            updated_entry = {
                "id": existing_portfolio.get("id", f"profile_portfolio_{int(datetime.now().timestamp())}") if existing_portfolio else f"profile_portfolio_{int(datetime.now().timestamp())}",
                "timestamp": existing_portfolio.get("timestamp", datetime.now().isoformat()) if existing_portfolio else datetime.now().isoformat(),
                "user_profile": user_profile,
                "portfolio_allocation": portfolio_allocation,
                "portfolio_summary": portfolio_summary,
                "risk_profile": user_profile.get("risk_tolerance", "moderate"),
                "total_allocation": sum(item.get("allocation_percentage", 0) for item in portfolio_allocation),
                "asset_classes": len(portfolio_allocation),
                "last_updated": datetime.now().isoformat(),
                "update_count": existing_portfolio.get("update_count", 0) + 1 if existing_portfolio else 1
            }
            
            # Save updated entry
            with open(self.portfolio_file, 'w') as f:
                json.dump(updated_entry, f, indent=2)
            
            logger.info("Updated profile portfolio in local storage")
            return updated_entry
            
        except Exception as e:
            logger.error(f"Error updating profile portfolio: {str(e)}")
            raise
    
    def clear_profile_portfolio(self) -> bool:
        """Clear stored profile portfolio"""
        try:
            if os.path.exists(self.portfolio_file):
                os.remove(self.portfolio_file)
                logger.info("Cleared profile portfolio")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error clearing profile portfolio: {str(e)}")
            return False
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get summary of stored profile portfolio"""
        try:
            portfolio = self.load_profile_portfolio()
            
            if not portfolio:
                return {
                    "has_portfolio": False,
                    "timestamp": None,
                    "risk_profile": None,
                    "total_allocation": 0,
                    "asset_classes": 0
                }
            
            return {
                "has_portfolio": True,
                "timestamp": portfolio.get("timestamp"),
                "last_updated": portfolio.get("last_updated"),
                "risk_profile": portfolio.get("risk_profile"),
                "total_allocation": portfolio.get("total_allocation", 0),
                "asset_classes": portfolio.get("asset_classes", 0),
                "update_count": portfolio.get("update_count", 0),
                "user_name": portfolio.get("user_profile", {}).get("name", "Unknown"),
                "loaded_from_storage": portfolio.get("loaded_from_storage", False)
            }
            
        except Exception as e:
            logger.error(f"Error getting portfolio summary: {str(e)}")
            return {"has_portfolio": False, "error": str(e)}
    
    def get_allocation_by_risk_profile(self, risk_tolerance: str) -> List[Dict[str, Any]]:
        """
        Get default allocation based on risk profile
        
        Args:
            risk_tolerance: Risk tolerance level (conservative, moderate, aggressive)
            
        Returns:
            Default allocation for the risk profile
        """
        try:
            # Default allocations based on risk profile
            allocations = {
                "conservative": [
                    {"asset_type": "bonds", "allocation_percentage": 45},
                    {"asset_type": "stocks", "allocation_percentage": 25},
                    {"asset_type": "cash", "allocation_percentage": 15},
                    {"asset_type": "real_estate", "allocation_percentage": 10},
                    {"asset_type": "etfs", "allocation_percentage": 5},
                    {"asset_type": "reits", "allocation_percentage": 0},
                    {"asset_type": "commodities", "allocation_percentage": 0},
                    {"asset_type": "cryptocurrency", "allocation_percentage": 0}
                ],
                "moderate": [
                    {"asset_type": "stocks", "allocation_percentage": 50},
                    {"asset_type": "bonds", "allocation_percentage": 25},
                    {"asset_type": "etfs", "allocation_percentage": 10},
                    {"asset_type": "real_estate", "allocation_percentage": 8},
                    {"asset_type": "cash", "allocation_percentage": 5},
                    {"asset_type": "reits", "allocation_percentage": 2},
                    {"asset_type": "commodities", "allocation_percentage": 0},
                    {"asset_type": "cryptocurrency", "allocation_percentage": 0}
                ],
                "aggressive": [
                    {"asset_type": "stocks", "allocation_percentage": 65},
                    {"asset_type": "bonds", "allocation_percentage": 15},
                    {"asset_type": "etfs", "allocation_percentage": 10},
                    {"asset_type": "real_estate", "allocation_percentage": 5},
                    {"asset_type": "cryptocurrency", "allocation_percentage": 3},
                    {"asset_type": "commodities", "allocation_percentage": 2},
                    {"asset_type": "reits", "allocation_percentage": 0},
                    {"asset_type": "cash", "allocation_percentage": 0}
                ]
            }
            
            return allocations.get(risk_tolerance.lower(), allocations["moderate"])
            
        except Exception as e:
            logger.error(f"Error getting allocation by risk profile: {str(e)}")
            return [] 