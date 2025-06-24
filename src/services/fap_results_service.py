"""
FAP Results Service for storing and retrieving Financial Analysis Pipeline results
"""

import json
import os
from datetime import datetime
from typing import Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)

class FAPResultsService:
    """Service for managing FAP results storage and retrieval"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.results_file = os.path.join(data_dir, "fap_results.json")
        self._ensure_data_directory()
    
    def _ensure_data_directory(self):
        """Ensure the data directory exists"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def save_fap_results(self, fap_context: Dict[str, Any], user_profile: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Save FAP results to local JSON file
        
        Args:
            fap_context: Complete FAP context with all analysis results
            user_profile: User profile information
            
        Returns:
            Saved results entry with metadata
        """
        try:
            # Create results entry
            results_entry = {
                "id": f"fap_{int(datetime.now().timestamp())}",
                "timestamp": datetime.now().isoformat(),
                "fap_context": fap_context,
                "user_profile": user_profile or {},
                "session_active": True
            }
            
            # Load existing results
            existing_results = self.load_fap_results()
            
            # Mark previous sessions as inactive
            if existing_results:
                existing_results["session_active"] = False
            
            # Save new results
            with open(self.results_file, 'w') as f:
                json.dump(results_entry, f, indent=2)
            
            logger.info("Saved FAP results to local storage")
            return results_entry
            
        except Exception as e:
            logger.error(f"Error saving FAP results: {str(e)}")
            raise
    
    def load_fap_results(self) -> Optional[Dict[str, Any]]:
        """
        Load the most recent FAP results from file
        
        Returns:
            FAP results if found, None otherwise
        """
        try:
            if not os.path.exists(self.results_file):
                return None
            
            with open(self.results_file, 'r') as f:
                results = json.load(f)
                
            # Mark as loaded (session restored)
            if results:
                results["session_restored"] = True
                
            return results
                
        except Exception as e:
            logger.error(f"Error loading FAP results: {str(e)}")
            return None
    
    def clear_fap_results(self) -> bool:
        """Clear stored FAP results"""
        try:
            if os.path.exists(self.results_file):
                os.remove(self.results_file)
                logger.info("Cleared FAP results")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error clearing FAP results: {str(e)}")
            return False
    
    def update_session_status(self, active: bool) -> bool:
        """Update session status without changing results"""
        try:
            results = self.load_fap_results()
            if results:
                results["session_active"] = active
                results["last_accessed"] = datetime.now().isoformat()
                
                with open(self.results_file, 'w') as f:
                    json.dump(results, f, indent=2)
                
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error updating session status: {str(e)}")
            return False
    
    def get_results_summary(self) -> Dict[str, Any]:
        """Get summary of stored FAP results"""
        try:
            results = self.load_fap_results()
            
            if not results:
                return {
                    "has_results": False,
                    "timestamp": None,
                    "session_active": False
                }
            
            return {
                "has_results": True,
                "timestamp": results.get("timestamp"),
                "session_active": results.get("session_active", False),
                "session_restored": results.get("session_restored", False),
                "user_profile": results.get("user_profile", {}),
                "fap_steps": {
                    "risk_assessment": bool(results.get("fap_context", {}).get("risk_assessment")),
                    "market_analysis": bool(results.get("fap_context", {}).get("market_analysis")),
                    "portfolio_allocation": bool(results.get("fap_context", {}).get("portfolio_allocation")),
                    "report": bool(results.get("fap_context", {}).get("report"))
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting results summary: {str(e)}")
            return {"has_results": False, "error": str(e)} 