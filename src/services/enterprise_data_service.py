"""
Enterprise Data Service - Optimized local file loading and caching for Enterprise mode
Avoids API calls by maintaining in-memory cache of all local data files
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class EnterpriseDataCache:
    """Enterprise data cache with timestamps"""
    user_profile: Optional[Dict[str, Any]] = None
    profile_portfolio: Optional[Dict[str, Any]] = None
    portfolio_holdings: Optional[List[Dict[str, Any]]] = None
    journal_entries: Optional[List[Dict[str, Any]]] = None
    fap_results: Optional[Dict[str, Any]] = None
    market_analysis: Optional[List[Dict[str, Any]]] = None
    transactions: Optional[List[Dict[str, Any]]] = None
    last_updated: Optional[str] = None
    cache_valid: bool = False

class EnterpriseDataService:
    """Enterprise-optimized data service with intelligent caching"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.cache = EnterpriseDataCache()
        self.file_paths = {
            'user_profile': os.path.join(data_dir, 'user_profile.json'),
            'profile_portfolio': os.path.join(data_dir, 'profile_portfolio.json'),
            'portfolio_holdings': os.path.join(data_dir, 'portfolio_holdings.json'),
            'journal': os.path.join(data_dir, 'journal.json'),
            'fap_results': os.path.join(data_dir, 'fap_results.json'),
            'market_analysis': os.path.join(data_dir, 'market_analysis.json'),
            'transactions': os.path.join(data_dir, 'transactions.json')
        }
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
        
        # Load initial cache
        self.refresh_cache()
        
        logger.info("🏢 Enterprise Data Service initialized with local file caching")

    def _load_json_file(self, file_path: str, default: Any = None) -> Any:
        """Safely load JSON file with fallback"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    logger.debug(f"✅ Loaded {file_path}")
                    return data
            else:
                logger.debug(f"📁 File not found: {file_path}, using default")
                return default
        except Exception as e:
            logger.error(f"❌ Error loading {file_path}: {str(e)}")
            return default

    def _save_json_file(self, file_path: str, data: Any) -> bool:
        """Safely save JSON file"""
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            logger.debug(f"💾 Saved {file_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Error saving {file_path}: {str(e)}")
            return False

    def refresh_cache(self) -> None:
        """Refresh all cached data from local files"""
        try:
            logger.info("🔄 Refreshing enterprise data cache from local files...")
            
            # Load all data files
            self.cache.user_profile = self._load_json_file(
                self.file_paths['user_profile'], 
                {}
            )
            
            self.cache.profile_portfolio = self._load_json_file(
                self.file_paths['profile_portfolio'], 
                {}
            )
            
            # Load portfolio holdings (handle both list and dict with "holdings" key)
            holdings_data = self._load_json_file(
                self.file_paths['portfolio_holdings'], 
                []
            )
            if isinstance(holdings_data, dict) and "holdings" in holdings_data:
                self.cache.portfolio_holdings = holdings_data["holdings"]
            elif isinstance(holdings_data, list):
                self.cache.portfolio_holdings = holdings_data
            else:
                self.cache.portfolio_holdings = []
            
            # Load journal entries (handle both list and dict with "entries" key)
            journal_data = self._load_json_file(
                self.file_paths['journal'], 
                []
            )
            if isinstance(journal_data, dict) and "entries" in journal_data:
                self.cache.journal_entries = journal_data["entries"]
            elif isinstance(journal_data, list):
                self.cache.journal_entries = journal_data
            else:
                self.cache.journal_entries = []
            
            self.cache.fap_results = self._load_json_file(
                self.file_paths['fap_results'], 
                {}
            )
            
            self.cache.market_analysis = self._load_json_file(
                self.file_paths['market_analysis'], 
                []
            )
            
            # Load transactions (handle both list and dict with "transactions" key)
            transactions_data = self._load_json_file(
                self.file_paths['transactions'], 
                []
            )
            if isinstance(transactions_data, dict) and "transactions" in transactions_data:
                self.cache.transactions = transactions_data["transactions"]
            elif isinstance(transactions_data, list):
                self.cache.transactions = transactions_data
            else:
                self.cache.transactions = []
            
            self.cache.last_updated = datetime.now().isoformat()
            self.cache.cache_valid = True
            
            logger.info("✅ Enterprise data cache refreshed successfully")
            
        except Exception as e:
            logger.error(f"❌ Error refreshing cache: {str(e)}")
            self.cache.cache_valid = False

    def get_comprehensive_dashboard_data(self) -> Dict[str, Any]:
        """Get all dashboard data in one call - optimized for enterprise mode"""
        if not self.cache.cache_valid:
            self.refresh_cache()
        
        # Build comprehensive user profile with all details
        user_profile = self.cache.user_profile or {}
        profile_portfolio = self.cache.profile_portfolio or {}
        
        # Debug: Check what we loaded
        logger.debug(f"🔍 Raw user_profile type: {type(user_profile)}")
        logger.debug(f"🔍 Raw user_profile data: {user_profile}")
        
        # Ensure user_profile is a dictionary
        if isinstance(user_profile, str):
            logger.warning("⚠️ User profile loaded as string, attempting to parse as JSON")
            try:
                import json
                user_profile = json.loads(user_profile)
            except Exception as e:
                logger.error(f"❌ Failed to parse user profile string as JSON: {e}")
                user_profile = {}
        
        # Enhanced profile data with enterprise details
        enhanced_profile = {
            "user_id": user_profile.get("user_id", "enterprise_user"),
            "name": user_profile.get("name", "Enterprise User"),
            "age": user_profile.get("age", 35),
            "income": user_profile.get("income", 75000),
            "risk_tolerance": user_profile.get("risk_tolerance", "moderate"),
            "investment_goal": user_profile.get("investment_goal", "long-term growth"),
            "investment_horizon": user_profile.get("investment_horizon", "long-term"),
            "created_at": user_profile.get("created_at", datetime.now().isoformat()),
            "last_updated": user_profile.get("last_updated", datetime.now().isoformat()),
            
            # Enterprise-specific enhancements
            "profile_completeness": self._calculate_profile_completeness(user_profile),
            "risk_score": self._calculate_risk_score(user_profile),
            "investment_capacity": self._calculate_investment_capacity(user_profile),
        }
        
        # Portfolio allocation from profile portfolio
        portfolio_allocation = {}
        if profile_portfolio.get("portfolio_allocation"):
            portfolio_allocation = profile_portfolio["portfolio_allocation"]
        
        # Portfolio summary with enterprise insights
        portfolio_summary = profile_portfolio.get("portfolio_summary", "No portfolio analysis available")
        
        # Recent FAP analysis
        fap_summary = None
        if self.cache.fap_results and self.cache.fap_results.get("report"):
            fap_summary = {
                "report": self.cache.fap_results["report"][:500] + "..." if len(self.cache.fap_results.get("report", "")) > 500 else self.cache.fap_results.get("report", ""),
                "timestamp": self.cache.fap_results.get("timestamp"),
                "risk_assessment": self.cache.fap_results.get("risk_assessment", {}),
                "portfolio_allocation": self.cache.fap_results.get("portfolio_allocation", {})
            }
        
        # Holdings summary with safe value calculation
        holdings_list = self.cache.portfolio_holdings or []
        total_value = 0
        for h in holdings_list:
            if isinstance(h, dict):
                # Calculate value from shares * purchase_price if value not directly available
                value = h.get("value", 0)
                if value == 0 and "shares" in h and "purchase_price" in h:
                    value = h.get("shares", 0) * h.get("purchase_price", 0)
                total_value += value
            # Skip if h is not a dict (shouldn't happen now, but safety check)
        
        holdings_summary = {
            "total_holdings": len(holdings_list),
            "holdings": holdings_list,
            "total_value": total_value
        }
        
        # Journal summary - safe slicing
        journal_entries = self.cache.journal_entries or []
        journal_summary = {
            "total_entries": len(journal_entries),
            "recent_entries": journal_entries[-3:] if journal_entries else [],
            "last_entry_date": journal_entries[-1].get("date") if journal_entries and len(journal_entries) > 0 else None
        }
        
        # Market analysis summary - handle both dict and list formats
        market_data = self.cache.market_analysis or {}
        if isinstance(market_data, dict):
            # If it's a dict, it's not a list of analyses but market data
            market_summary = {
                "total_analyses": 0,
                "recent_analyses": [],
                "market_data": market_data  # Include the actual market data (indices, etc.)
            }
        else:
            # If it's a list, treat as analyses
            market_summary = {
                "total_analyses": len(market_data),
                "recent_analyses": market_data[-5:] if market_data else [],
                "market_data": {}
            }
        
        return {
            "no_profile": not bool(enhanced_profile.get("name") and enhanced_profile.get("name") != "Enterprise User"),
            "user_profile": enhanced_profile,
            "portfolio_allocation": portfolio_allocation,
            "portfolio_summary": portfolio_summary,
            "fap_analysis": fap_summary,
            "holdings": holdings_summary,
            "journal": journal_summary,
            "market_analysis": market_summary,
            "cache_info": {
                "last_updated": self.cache.last_updated,
                "cache_valid": self.cache.cache_valid,
                "data_sources": "local_files_only"
            },
            "enterprise_mode": True
        }

    def _calculate_profile_completeness(self, profile: Dict[str, Any]) -> float:
        """Calculate profile completeness percentage"""
        required_fields = ["name", "age", "income", "risk_tolerance", "investment_goal", "investment_horizon"]
        completed_fields = sum(1 for field in required_fields if profile.get(field))
        return (completed_fields / len(required_fields)) * 100

    def _calculate_risk_score(self, profile: Dict[str, Any]) -> int:
        """Calculate numerical risk score (1-10)"""
        risk_tolerance = profile.get("risk_tolerance", "moderate").lower()
        age = profile.get("age", 35)
        
        base_score = {
            "conservative": 3,
            "moderate": 6,
            "aggressive": 9
        }.get(risk_tolerance, 6)
        
        # Adjust for age (younger = higher risk capacity)
        if age < 30:
            base_score += 1
        elif age > 50:
            base_score -= 1
            
        return max(1, min(10, base_score))

    def _calculate_investment_capacity(self, profile: Dict[str, Any]) -> str:
        """Calculate investment capacity based on income and age"""
        income = profile.get("income", 0)
        age = profile.get("age", 35)
        
        if income < 40000:
            return "Conservative"
        elif income < 80000:
            return "Moderate" 
        elif income < 150000:
            return "Substantial"
        else:
            return "High"

    def get_cached_data(self, data_type: str) -> Any:
        """Get specific cached data type"""
        if not self.cache.cache_valid:
            self.refresh_cache()
            
        return getattr(self.cache, data_type, None)

    def update_cache_data(self, data_type: str, data: Any) -> bool:
        """Update specific cached data and save to file"""
        try:
            # Update cache
            setattr(self.cache, data_type, data)
            
            # Save to file
            file_path = self.file_paths.get(data_type)
            if file_path:
                success = self._save_json_file(file_path, data)
                if success:
                    self.cache.last_updated = datetime.now().isoformat()
                    logger.info(f"📊 Updated enterprise cache: {data_type}")
                return success
            return False
        except Exception as e:
            logger.error(f"❌ Error updating cache {data_type}: {str(e)}")
            return False

    def invalidate_cache(self) -> None:
        """Invalidate cache to force refresh on next access"""
        self.cache.cache_valid = False
        logger.info("🔄 Enterprise cache invalidated")

# Global enterprise data service instance
enterprise_data_service = EnterpriseDataService() 