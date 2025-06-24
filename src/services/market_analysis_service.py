"""
Market Analysis Service for storing and retrieving analysis results
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class MarketAnalysisService:
    """Service for managing market analysis storage and retrieval"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.analysis_file = os.path.join(data_dir, "market_analysis.json")
        self._ensure_data_directory()
    
    def _ensure_data_directory(self):
        """Ensure the data directory exists"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def save_analysis(self, symbol: str, period: str, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save market analysis result to local JSON file
        
        Args:
            symbol: Stock/asset symbol (e.g., 'GC=F', '^GSPC')
            period: Time period (e.g., '6mo', '1y')
            analysis_data: Complete analysis data including AI response
            
        Returns:
            Saved analysis entry with metadata
        """
        try:
            # Load existing analyses
            analyses = self.load_all_analyses()
            
            # Create analysis entry
            analysis_entry = {
                "id": f"{symbol}_{period}_{int(datetime.now().timestamp())}",
                "symbol": symbol,
                "period": period,
                "timestamp": datetime.now().isoformat(),
                "analysis_data": analysis_data
            }
            
            # Update or add analysis (replace if same symbol+period exists)
            analysis_key = f"{symbol}_{period}"
            analyses[analysis_key] = analysis_entry
            
            # Save to file
            with open(self.analysis_file, 'w') as f:
                json.dump(analyses, f, indent=2)
            
            logger.info(f"Saved market analysis for {symbol} ({period})")
            return analysis_entry
            
        except Exception as e:
            logger.error(f"Error saving market analysis: {str(e)}")
            raise
    
    def load_analysis(self, symbol: str, period: str) -> Optional[Dict[str, Any]]:
        """
        Load specific market analysis by symbol and period
        
        Args:
            symbol: Stock/asset symbol
            period: Time period
            
        Returns:
            Analysis data if found, None otherwise
        """
        try:
            analyses = self.load_all_analyses()
            analysis_key = f"{symbol}_{period}"
            return analyses.get(analysis_key)
            
        except Exception as e:
            logger.error(f"Error loading market analysis for {symbol} ({period}): {str(e)}")
            return None
    
    def load_all_analyses(self) -> Dict[str, Any]:
        """Load all market analyses from file"""
        try:
            if not os.path.exists(self.analysis_file):
                return {}
            
            with open(self.analysis_file, 'r') as f:
                return json.load(f)
                
        except Exception as e:
            logger.error(f"Error loading market analyses: {str(e)}")
            return {}
    
    def get_recent_analyses(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get most recent market analyses
        
        Args:
            limit: Maximum number of analyses to return
            
        Returns:
            List of recent analyses sorted by timestamp (newest first)
        """
        try:
            analyses = self.load_all_analyses()
            
            # Convert to list and sort by timestamp
            analysis_list = list(analyses.values())
            analysis_list.sort(key=lambda x: x['timestamp'], reverse=True)
            
            return analysis_list[:limit]
            
        except Exception as e:
            logger.error(f"Error getting recent analyses: {str(e)}")
            return []
    
    def delete_analysis(self, symbol: str, period: str) -> bool:
        """
        Delete specific market analysis
        
        Args:
            symbol: Stock/asset symbol
            period: Time period
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            analyses = self.load_all_analyses()
            analysis_key = f"{symbol}_{period}"
            
            if analysis_key in analyses:
                del analyses[analysis_key]
                
                with open(self.analysis_file, 'w') as f:
                    json.dump(analyses, f, indent=2)
                
                logger.info(f"Deleted market analysis for {symbol} ({period})")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deleting market analysis: {str(e)}")
            return False
    
    def clear_all_analyses(self) -> bool:
        """Clear all stored analyses"""
        try:
            with open(self.analysis_file, 'w') as f:
                json.dump({}, f)
            
            logger.info("Cleared all market analyses")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing analyses: {str(e)}")
            return False
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """Get summary of stored analyses"""
        try:
            analyses = self.load_all_analyses()
            
            return {
                "total_analyses": len(analyses),
                "symbols": list(set(analysis['symbol'] for analysis in analyses.values())),
                "periods": list(set(analysis['period'] for analysis in analyses.values())),
                "latest_timestamp": max(
                    (analysis['timestamp'] for analysis in analyses.values()),
                    default=None
                )
            }
            
        except Exception as e:
            logger.error(f"Error getting analysis summary: {str(e)}")
            return {"total_analyses": 0, "symbols": [], "periods": [], "latest_timestamp": None} 