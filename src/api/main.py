"""
Enhanced FastAPI application with Enterprise Features
Integrates Responsible AI Layer, Plugin Architecture, and Dynamic Tool Discovery
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import os
from dotenv import load_dotenv
import logging
import uuid
from fastapi import Path
import re
from fastapi.responses import JSONResponse
from datetime import datetime

# Import existing services
from src.agents import CoordinatorAgent
from langchain_openai import ChatOpenAI
from src.services.user_profile_service import UserProfileService
from src.models.user_profile import UserProfile, InvestmentPreference
from src.models.fap_context import FAPContext
from src.agents.fap_pipeline import run_fap_pipeline
from src.models.portfolio import PortfolioHolding
from src.services.portfolio_service import PortfolioService
from src.models.journal import JournalEntry
from src.services.journal_service import JournalService
from src.services.market_data_service import MarketDataService
from src.services.market_analysis_service import MarketAnalysisService
from src.services.fap_results_service import FAPResultsService
from src.services.profile_portfolio_service import ProfilePortfolioService
from src.services.enterprise_data_service import enterprise_data_service

# Import legacy models for compatibility
class ChatResponse(BaseModel):
    response: str
    error: Optional[str] = None

class UserProfileRequest(BaseModel):
    name: str
    age: int
    income: float
    risk_tolerance: str
    investment_goal: str
    investment_horizon: str

class UserProfileResponse(BaseModel):
    user_id: str
    name: str
    risk_tolerance: str
    investment_goal: str
    investment_horizon: str
    preferences: List[Dict]

# Import enterprise features
from src.agents.plugin_enabled_agent import DynamicFinancialAgent
from src.services.responsible_ai_service import ResponsibleAIService, RiskLevel
from src.services.plugin_registry import plugin_registry, PluginCategory

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AgenticAI Enterprise Financial Advisor API",
    description="Enterprise-grade Financial Investment Advisor with Responsible AI and Plugin Architecture",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services and agents
user_profile_service = UserProfileService()
portfolio_service = PortfolioService()
journal_service = JournalService()
market_data_service = MarketDataService()
market_analysis_service = MarketAnalysisService()
fap_results_service = FAPResultsService()
profile_portfolio_service = ProfilePortfolioService()
responsible_ai_service = ResponsibleAIService()

# Initialize enterprise agent (replaces basic coordinator)
enterprise_coordinator = DynamicFinancialAgent(
    plugin_categories=[
        PluginCategory.MARKET_DATA,
        PluginCategory.AI_ANALYSIS,
        PluginCategory.COMPLIANCE,
        PluginCategory.RISK_ASSESSMENT
    ],
    enable_responsible_ai=True,
    enable_input_moderation=True,
    enable_output_moderation=True,
    enable_hallucination_detection=True,
    block_high_risk=True
)

# Enhanced request/response models
class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None
    enable_compliance_check: bool = True
    risk_tolerance: Optional[str] = "medium"

class EnterpriseChatResponse(BaseModel):
    response: str
    moderation_passed: bool
    risk_level: str
    compliance_issues: List[str] = []
    used_tools: List[str] = []
    confidence_score: Optional[float] = None
    disclaimer_added: bool = False
    error: Optional[str] = None

class PluginManagementRequest(BaseModel):
    plugin_name: str
    action: str  # load, unload, reload, configure
    config: Optional[Dict[str, Any]] = None

class PluginStatusResponse(BaseModel):
    plugin_name: str
    status: str
    tools_count: int
    category: str
    version: str
    last_updated: str

class ModerationRequest(BaseModel):
    content: str
    content_type: str = "general"  # general, investment_advice, portfolio_recommendation

class ModerationResponse(BaseModel):
    passed: bool
    risk_level: str
    issues: List[str]
    sanitized_content: Optional[str] = None
    suggestions: List[str] = []

class ComplianceCheckRequest(BaseModel):
    content: str
    advice_type: str = "investment_recommendation"
    user_profile: Optional[Dict[str, Any]] = None

class ComplianceCheckResponse(BaseModel):
    compliant: bool
    required_disclosures: List[str]
    regulatory_guidance: str
    suitability_assessment: Optional[str] = None
    recommendations: List[str]

# Startup event to initialize plugins
@app.on_event("startup")
async def startup_event():
    """Initialize enterprise features on startup"""
    try:
        logger.info("🏢 Starting Enterprise AgenticAI...")
        
        # Initialize plugin registry
        await plugin_registry.initialize_all_plugins()
        
        # Get plugin stats
        stats = plugin_registry.get_plugin_stats()
        logger.info(f"📊 Loaded {stats['active_plugins']} plugins with {stats['total_tools']} tools")
        
        # Initialize enterprise coordinator with latest tools
        await enterprise_coordinator.refresh_plugin_tools()
        
        logger.info("✅ Enterprise AgenticAI initialized successfully!")
        
    except Exception as e:
        logger.error(f"❌ Startup error: {str(e)}")

# ==============================================================================
# ENHANCED EXISTING ENDPOINTS
# ==============================================================================

@app.post("/api/v2/chat", response_model=EnterpriseChatResponse)
async def enterprise_chat(request: ChatRequest):
    """Enhanced chat with enterprise features"""
    try:
        logger.info(f"🤖 Processing enterprise chat: {request.message[:50]}...")
        
        # Pre-chat moderation report
        input_moderation = await responsible_ai_service.moderate_input(request.message)
        
        if not input_moderation.passed and request.enable_compliance_check:
            return EnterpriseChatResponse(
                response="I cannot process this request due to safety guidelines. Please rephrase your question.",
                moderation_passed=False,
                risk_level=input_moderation.risk_level.value,
                compliance_issues=input_moderation.issues,
                used_tools=[],
                error="Input blocked by moderation"
            )
        
        # Process with enterprise coordinator
        response = await enterprise_coordinator.process_message(
            input_moderation.sanitized_content or request.message
        )
        
        # Post-chat moderation
        output_moderation = await responsible_ai_service.moderate_output(response, request.message)
        
        # Hallucination detection
        hallucination_result = await responsible_ai_service.detect_hallucinations(response, request.message)
        
        # Get tool usage information
        tool_manifest = enterprise_coordinator.get_tool_manifest()
        used_tools = [tool["name"] for tool in tool_manifest["tools"][:5]]  # Show first 5 tools
        
        return EnterpriseChatResponse(
            response=output_moderation.sanitized_content or response,
            moderation_passed=output_moderation.passed,
            risk_level=output_moderation.risk_level.value,
            compliance_issues=output_moderation.issues,
            used_tools=used_tools,
            confidence_score=hallucination_result.confidence_score,
            disclaimer_added=output_moderation.sanitized_content != response
        )
        
    except Exception as e:
        logger.error(f"Error in enterprise chat: {str(e)}")
        return EnterpriseChatResponse(
            response="I apologize for the technical difficulty. Please try again.",
            moderation_passed=False,
            risk_level="high",
            compliance_issues=["System error occurred"],
            used_tools=[],
            error=str(e)
        )

@app.post("/api/v2/profile", response_model=UserProfileResponse)
async def create_enterprise_profile(request: UserProfileRequest):
    """Create profile with enterprise compliance checking"""
    try:
        # Validate profile data with compliance rules
        compliance_check = await responsible_ai_service.moderate_input(
            f"Creating profile for {request.name}, age {request.age}, income {request.income}, risk tolerance {request.risk_tolerance}"
        )
        
        if not compliance_check.passed:
            logger.warning(f"Profile creation blocked: {compliance_check.issues}")
            raise HTTPException(
                status_code=400, 
                detail=f"Profile validation failed: {', '.join(compliance_check.issues)}"
            )
        
        # Create profile with enterprise features
        user_id = str(uuid.uuid4())
        profile = user_profile_service.create_default_profile(
            user_id=user_id,
            name=request.name,
            age=request.age,
            income=request.income
        )
        
        profile.risk_tolerance = request.risk_tolerance
        profile.investment_goal = request.investment_goal
        profile.investment_horizon = request.investment_horizon
        
        if not user_profile_service.save_profile(profile):
            raise HTTPException(status_code=500, detail="Failed to save profile")
        
        # Generate initial enterprise report
        enterprise_report = await enterprise_coordinator.process_message(
            f"Generate initial investment guidance for {profile.name}, age {profile.age}, "
            f"income ${profile.income}, {profile.risk_tolerance} risk tolerance"
        )
        
        return UserProfileResponse(
            user_id=profile.user_id,
            name=profile.name,
            risk_tolerance=profile.risk_tolerance,
            investment_goal=profile.investment_goal,
            investment_horizon=profile.investment_horizon,
            preferences=[p.model_dump() for p in profile.preferences]
        )
        
    except Exception as e:
        logger.error(f"Error creating enterprise profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==============================================================================
# NEW ENTERPRISE ENDPOINTS
# ==============================================================================

@app.get("/api/v2/enterprise/status")
async def get_enterprise_status():
    """Get enterprise system status"""
    try:
        plugin_stats = plugin_registry.get_plugin_stats()
        tool_manifest = enterprise_coordinator.get_tool_manifest()
        
        return {
            "status": "operational",
            "version": "2.0.0",
            "features": {
                "responsible_ai": True,
                "plugin_architecture": True,
                "dynamic_tools": True,
                "compliance_checking": True
            },
            "plugins": plugin_stats,
            "tools": tool_manifest,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting enterprise status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v2/plugins/manage", response_model=PluginStatusResponse)
async def manage_plugin(request: PluginManagementRequest):
    """Manage plugins (load, unload, reload, configure)"""
    try:
        plugin_name = request.plugin_name
        action = request.action.lower()
        
        if action == "load":
            success = await plugin_registry.load_plugin(plugin_name)
            if success:
                await enterprise_coordinator.refresh_plugin_tools()
        elif action == "unload":
            success = await plugin_registry.unload_plugin(plugin_name)
            if success:
                await enterprise_coordinator.refresh_plugin_tools()
        elif action == "reload":
            success = await plugin_registry.reload_plugin(plugin_name)
            if success:
                await enterprise_coordinator.refresh_plugin_tools()
        elif action == "configure":
            if request.config:
                plugin_registry.update_plugin_config(plugin_name, request.config)
                success = await plugin_registry.reload_plugin(plugin_name)
            else:
                raise HTTPException(status_code=400, detail="Configuration required for configure action")
        else:
            raise HTTPException(status_code=400, detail="Invalid action. Use: load, unload, reload, configure")
        
        # Get updated plugin info
        plugin_info = plugin_registry.get_plugin_info(plugin_name)
        if not plugin_info:
            raise HTTPException(status_code=404, detail="Plugin not found")
        
        return PluginStatusResponse(
            plugin_name=plugin_name,
            status=plugin_info.status.value,
            tools_count=len(plugin_info.tools),
            category=plugin_info.metadata.category.value,
            version=plugin_info.metadata.version,
            last_updated=plugin_info.load_time.isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error managing plugin {request.plugin_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v2/plugins/available")
async def get_available_plugins():
    """Get all available plugins and their status"""
    try:
        all_plugins = plugin_registry.get_all_plugins()
        
        plugins_list = []
        for plugin_name, plugin_info in all_plugins.items():
            plugins_list.append({
                "name": plugin_name,
                "status": plugin_info.status.value,
                "category": plugin_info.metadata.category.value,
                "version": plugin_info.metadata.version,
                "description": plugin_info.metadata.description,
                "tools_count": len(plugin_info.tools),
                "load_time": plugin_info.load_time.isoformat(),
                "error_message": plugin_info.error_message
            })
        
        return {
            "plugins": plugins_list,
            "total_plugins": len(plugins_list),
            "active_plugins": len([p for p in plugins_list if p["status"] == "active"])
        }
        
    except Exception as e:
        logger.error(f"Error getting available plugins: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v2/moderation/check", response_model=ModerationResponse)
async def check_content_moderation(request: ModerationRequest):
    """Check content with responsible AI moderation"""
    try:
        if request.content_type == "input":
            moderation_result = await responsible_ai_service.moderate_input(request.content)
        else:
            moderation_result = await responsible_ai_service.moderate_output(request.content)
        
        suggestions = []
        if not moderation_result.passed:
            suggestions = [
                "Remove any prohibited financial terms",
                "Add appropriate disclaimers",
                "Consider compliance requirements",
                "Verify information accuracy"
            ]
        
        return ModerationResponse(
            passed=moderation_result.passed,
            risk_level=moderation_result.risk_level.value,
            issues=moderation_result.issues,
            sanitized_content=moderation_result.sanitized_content,
            suggestions=suggestions
        )
        
    except Exception as e:
        logger.error(f"Error in content moderation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v2/compliance/check", response_model=ComplianceCheckResponse)
async def check_compliance(request: ComplianceCheckRequest):
    """Check content for financial compliance"""
    try:
        # Use compliance plugin if available
        compliance_tools = plugin_registry.get_available_tools(PluginCategory.COMPLIANCE)
        
        if not compliance_tools:
            return ComplianceCheckResponse(
                compliant=False,
                required_disclosures=["Plugin not available"],
                regulatory_guidance="Compliance plugin not loaded",
                recommendations=["Load compliance plugin for detailed checking"]
            )
        
        # Simulate compliance check (in real implementation, would use actual compliance plugin)
        compliance_result = await responsible_ai_service.moderate_output(request.content)
        
        required_disclosures = [
            "This is not personalized financial advice",
            "Past performance does not guarantee future results", 
            "Investment involves risk of loss",
            "Consult with a qualified financial advisor"
        ]
        
        regulatory_guidance = f"For {request.advice_type}, ensure proper disclosures and suitability assessment."
        
        recommendations = []
        if not compliance_result.passed:
            recommendations = [
                "Add required financial disclaimers",
                "Perform suitability assessment",
                "Review regulatory requirements",
                "Consider fiduciary obligations"
            ]
        
        return ComplianceCheckResponse(
            compliant=compliance_result.passed,
            required_disclosures=required_disclosures,
            regulatory_guidance=regulatory_guidance,
            suitability_assessment="Further review required" if not compliance_result.passed else "Initial check passed",
            recommendations=recommendations
        )
        
    except Exception as e:
        logger.error(f"Error in compliance check: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v2/tools/manifest")
async def get_tools_manifest():
    """Get detailed manifest of all available tools"""
    try:
        manifest = enterprise_coordinator.get_tool_manifest()
        
        # Add plugin source information
        enhanced_manifest = {
            **manifest,
            "plugin_sources": {},
            "categories_detail": {}
        }
        
        # Get detailed plugin information
        all_plugins = plugin_registry.get_all_plugins()
        for plugin_name, plugin_info in all_plugins.items():
            enhanced_manifest["plugin_sources"][plugin_name] = {
                "status": plugin_info.status.value,
                "category": plugin_info.metadata.category.value,
                "description": plugin_info.metadata.description,
                "version": plugin_info.metadata.version,
                "tools": [tool.name for tool in plugin_info.tools]
            }
        
        # Category details
        for category in PluginCategory:
            tools = plugin_registry.get_available_tools(category)
            enhanced_manifest["categories_detail"][category.value] = {
                "tools_count": len(tools),
                "tools": [{"name": tool.name, "description": tool.description} for tool in tools]
            }
        
        return enhanced_manifest
        
    except Exception as e:
        logger.error(f"Error getting tools manifest: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v2/analytics/usage")
async def get_usage_analytics():
    """Get usage analytics for enterprise features"""
    try:
        # Get moderation statistics
        moderation_stats = responsible_ai_service.get_moderation_stats()
        
        # Get plugin statistics  
        plugin_stats = plugin_registry.get_plugin_stats()
        
        # Get tool usage (placeholder - would track in real implementation)
        tool_usage = await enterprise_coordinator.analyze_tool_usage()
        
        return {
            "moderation": moderation_stats,
            "plugins": plugin_stats,
            "tools": tool_usage,
            "timestamp": datetime.now().isoformat(),
            "system_health": "operational"
        }
        
    except Exception as e:
        logger.error(f"Error getting usage analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==============================================================================
# HEALTH AND MONITORING
# ==============================================================================

@app.get("/api/v2/health/enterprise")
async def enterprise_health_check():
    """Comprehensive enterprise health check"""
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {}
        }
        
        # Check plugin registry
        try:
            plugin_stats = plugin_registry.get_plugin_stats()
            health_status["components"]["plugins"] = {
                "status": "healthy",
                "active_plugins": plugin_stats["active_plugins"],
                "total_tools": plugin_stats["total_tools"]
            }
        except Exception as e:
            health_status["components"]["plugins"] = {"status": "unhealthy", "error": str(e)}
            health_status["status"] = "degraded"
        
        # Check responsible AI service
        try:
            # Simple test of responsible AI
            test_moderation = await responsible_ai_service.moderate_input("test message")
            health_status["components"]["responsible_ai"] = {
                "status": "healthy",
                "moderation_working": True
            }
        except Exception as e:
            health_status["components"]["responsible_ai"] = {"status": "unhealthy", "error": str(e)}
            health_status["status"] = "degraded"
        
        # Check enterprise coordinator
        try:
            tool_count = len(enterprise_coordinator.tools)
            health_status["components"]["enterprise_coordinator"] = {
                "status": "healthy",
                "tools_loaded": tool_count
            }
        except Exception as e:
            health_status["components"]["enterprise_coordinator"] = {"status": "unhealthy", "error": str(e)}
            health_status["status"] = "degraded"
        
        return health_status
        
    except Exception as e:
        logger.error(f"Error in enterprise health check: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# ==============================================================================
# V1 API COMPATIBILITY LAYER
# ==============================================================================

@app.get("/api/v1/dashboard/data")
async def get_dashboard_data():
    """Get complete dashboard data in one call - Enterprise optimized with zero API calls"""
    try:
        logger.info("🏢 Loading complete dashboard data from enterprise cache (zero API calls)...")
        comprehensive_data = enterprise_data_service.get_comprehensive_dashboard_data()
        
        # Return everything the dashboard needs in one response
        return {
            "dashboard_type": "enterprise_cached",
            "profile": {
                "no_profile": comprehensive_data["no_profile"],
                "user_id": comprehensive_data["user_profile"]["user_id"],
                "name": comprehensive_data["user_profile"]["name"],
                "age": comprehensive_data["user_profile"]["age"],
                "income": comprehensive_data["user_profile"]["income"],
                "risk_tolerance": comprehensive_data["user_profile"]["risk_tolerance"],
                "investment_goal": comprehensive_data["user_profile"]["investment_goal"],
                "investment_horizon": comprehensive_data["user_profile"]["investment_horizon"],
                "profile_completeness": comprehensive_data["user_profile"]["profile_completeness"],
                "risk_score": comprehensive_data["user_profile"]["risk_score"],
                "investment_capacity": comprehensive_data["user_profile"]["investment_capacity"],
            },
            "portfolio": {
                "allocation": comprehensive_data["portfolio_allocation"],
                "summary": comprehensive_data["portfolio_summary"],
                "holdings": comprehensive_data["holdings"],
            },
            "analysis": {
                "fap_results": comprehensive_data["fap_analysis"],
                "journal": comprehensive_data["journal"],
                "market_analysis": comprehensive_data["market_analysis"],
            },
            "cache_info": {
                "last_updated": comprehensive_data["cache_info"]["last_updated"],
                "data_source": "enterprise_file_cache_only",
                "api_calls_made": 0
            }
        }
        
    except Exception as e:
        logger.error(f"Error loading enterprise dashboard data: {str(e)}")
        return {
            "dashboard_type": "error",
            "profile": {"no_profile": True},
            "error": str(e),
            "cache_info": {"data_source": "error", "api_calls_made": 0}
        }

@app.get("/api/v1/portfolio/summary")
async def get_portfolio_summary():
    """Get user's portfolio summary - Enterprise optimized with local file caching"""
    try:
        # Use enterprise data service for optimized local file loading
        logger.info("🏢 Loading enterprise dashboard data from local files...")
        comprehensive_data = enterprise_data_service.get_comprehensive_dashboard_data()
        
        # Debug: Check data types
        logger.debug(f"🔍 User profile type: {type(comprehensive_data['user_profile'])}")
        logger.debug(f"🔍 User profile data: {comprehensive_data['user_profile']}")
        
        # Return enhanced data with all profile details
        return {
            "no_profile": comprehensive_data["no_profile"],
            "user_id": comprehensive_data["user_profile"]["user_id"],
            "name": comprehensive_data["user_profile"]["name"],
            "age": comprehensive_data["user_profile"]["age"],
            "income": comprehensive_data["user_profile"]["income"],
            "risk_tolerance": comprehensive_data["user_profile"]["risk_tolerance"],
            "investment_goal": comprehensive_data["user_profile"]["investment_goal"],
            "investment_horizon": comprehensive_data["user_profile"]["investment_horizon"],
            
            # Enterprise enhancements
            "profile_completeness": comprehensive_data["user_profile"]["profile_completeness"],
            "risk_score": comprehensive_data["user_profile"]["risk_score"],
            "investment_capacity": comprehensive_data["user_profile"]["investment_capacity"],
            
            # Portfolio data
            "portfolio_allocation": comprehensive_data["portfolio_allocation"],
            "portfolio_summary": comprehensive_data["portfolio_summary"],
            
            # Additional data for dashboard
            "fap_analysis": comprehensive_data["fap_analysis"],
            "holdings_summary": comprehensive_data["holdings"],
            "journal_summary": comprehensive_data["journal"],
            "market_analysis_summary": comprehensive_data["market_analysis"],
            
            # Cache info for debugging
            "cache_info": comprehensive_data["cache_info"],
            "enterprise_mode": True,
            "data_source": "enterprise_local_cache"
        }
        
    except Exception as e:
        logger.error(f"Error getting enterprise portfolio summary: {str(e)}")
        logger.error(f"Error details: {type(e).__name__}: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        # Fallback to standard service
        try:
            summary = user_profile_service.get_portfolio_summary()
            if "error" in summary and summary["error"] == "No user profile found":
                return {"no_profile": True}
            if "error" in summary:
                raise HTTPException(status_code=404, detail=summary["error"])
            return summary
        except Exception as fallback_error:
            logger.error(f"Fallback also failed: {str(fallback_error)}")
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "mode": "enterprise", "features": ["enterprise_chat", "plugin_manager", "responsible_ai", "compliance_checking"]}

@app.get("/api/v1/backend/mode")
async def get_backend_mode():
    """Get backend mode information"""
    return {
        "mode": "enterprise",
        "version": "2.0.0",
        "features": {
            "enterprise_chat": True,
            "plugin_manager": True,
            "responsible_ai": True,
            "compliance_checking": True,
            "advanced_analytics": True
        },
        "description": "Enterprise Financial Investment Advisor with AI Compliance"
    }

@app.get("/api/v1/portfolio/data")
async def get_portfolio_data():
    """Get complete portfolio tab data in one call - Enterprise optimized with zero API calls"""
    try:
        logger.info("🏢 Loading portfolio tab data from enterprise cache (zero API calls)...")
        
        # Get cached data
        holdings = enterprise_data_service.get_cached_data('portfolio_holdings') or []
        transactions = enterprise_data_service.get_cached_data('transactions') or []
        profile_portfolio = enterprise_data_service.get_cached_data('profile_portfolio') or {}
        
        # Calculate portfolio summary
        total_value = sum(h.get("shares", 0) * h.get("purchase_price", 0) for h in holdings if isinstance(h, dict))
        
        return {
            "tab_type": "portfolio_cached",
            "holdings": {
                "list": holdings,
                "total_holdings": len(holdings),
                "total_value": total_value
            },
            "transactions": {
                "list": transactions,
                "total_transactions": len(transactions)
            },
            "allocation": profile_portfolio.get("portfolio_allocation", []),
            "summary": profile_portfolio.get("portfolio_summary", ""),
            "cache_info": {
                "data_source": "enterprise_file_cache_only",
                "api_calls_made": 0
            }
        }
        
    except Exception as e:
        logger.error(f"Error loading enterprise portfolio data: {str(e)}")
        return {
            "tab_type": "error",
            "error": str(e),
            "cache_info": {"data_source": "error", "api_calls_made": 0}
        }

@app.get("/api/v1/portfolio/holdings")
async def get_portfolio_holdings():
    """Get portfolio holdings - Enterprise optimized from cache"""
    try:
        # Use cached data to avoid file I/O on tab switches
        holdings = enterprise_data_service.get_cached_data('portfolio_holdings') or []
        logger.debug(f"🏢 Retrieved {len(holdings)} holdings from enterprise cache")
        return {"holdings": holdings, "data_source": "enterprise_cache"}
    except Exception as e:
        logger.error(f"Error getting enterprise portfolio holdings: {str(e)}")
        # Fallback to standard service
        try:
            holdings = portfolio_service.get_holdings()
            return {"holdings": holdings}
        except Exception as fallback_error:
            logger.error(f"Holdings fallback failed: {str(fallback_error)}")
            raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/portfolio/holdings")
async def add_portfolio_holding(holding: PortfolioHolding):
    """Add a portfolio holding"""
    try:
        portfolio_service.add_holding(holding)
        return {"status": "success", "message": "Holding added successfully"}
    except Exception as e:
        logger.error(f"Error adding portfolio holding: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/portfolio/transactions")
async def get_transactions():
    """Get portfolio transactions"""
    try:
        return {"transactions": []}
    except Exception as e:
        logger.error(f"Error getting transactions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/journal/data")
async def get_journal_data():
    """Get complete journal tab data in one call - Enterprise optimized with zero API calls"""
    try:
        logger.info("🏢 Loading journal tab data from enterprise cache (zero API calls)...")
        
        # Get cached data
        journal_entries = enterprise_data_service.get_cached_data('journal_entries') or []
        
        return {
            "tab_type": "journal_cached",
            "entries": {
                "list": journal_entries,
                "total_entries": len(journal_entries),
                "recent_entries": journal_entries[-5:] if journal_entries else []
            },
            "cache_info": {
                "data_source": "enterprise_file_cache_only",
                "api_calls_made": 0
            }
        }
        
    except Exception as e:
        logger.error(f"Error loading enterprise journal data: {str(e)}")
        return {
            "tab_type": "error",
            "error": str(e),
            "cache_info": {"data_source": "error", "api_calls_made": 0}
        }

@app.get("/api/v1/journal")
async def get_journal_entries():
    """Get journal entries - Enterprise optimized from cache"""
    try:
        # Use cached data to avoid file I/O on tab switches
        entries = enterprise_data_service.get_cached_data('journal_entries') or []
        logger.debug(f"🏢 Retrieved {len(entries)} journal entries from enterprise cache")
        return {"entries": entries, "data_source": "enterprise_cache"}
    except Exception as e:
        logger.error(f"Error getting enterprise journal entries: {str(e)}")
        # Fallback to standard service
        try:
            entries = journal_service.get_entries()
            return {"entries": entries}
        except Exception as fallback_error:
            logger.error(f"Journal fallback failed: {str(fallback_error)}")
            raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/journal")
async def add_journal_entry(entry: JournalEntry):
    """Add a journal entry"""
    try:
        journal_service.add_entry(entry)
        return {"status": "success", "message": "Journal entry added successfully"}
    except Exception as e:
        logger.error(f"Error adding journal entry: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/market/quote/{symbol}")
async def get_market_quote(symbol: str):
    """Get market quote for a symbol"""
    try:
        quote_data = await market_data_service.get_quote(symbol)
        return quote_data
    except Exception as e:
        logger.error(f"Error getting market quote for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/market/indices")
async def get_market_indices():
    """Get market indices"""
    try:
        indices_data = await market_data_service.get_major_indices()
        return {"indices": indices_data}
    except Exception as e:
        logger.error(f"Error getting market indices: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/market/historical/{symbol}")
async def get_historical_market_data(symbol: str, period: str = "1d"):
    """Get historical market data"""
    try:
        historical_data = await market_data_service.get_historical_data(symbol, period)
        return historical_data
    except Exception as e:
        logger.error(f"Error getting historical data for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/market/analysis/recent")
async def get_recent_market_analyses(limit: int = 10):
    """Get recent market analyses"""
    try:
        analyses = market_analysis_service.get_recent_analyses(limit)
        return {"analyses": analyses}
    except Exception as e:
        logger.error(f"Error getting recent market analyses: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/fap/results")
async def get_fap_results():
    """Get FAP results - Enterprise optimized from cache"""
    try:
        # Use cached data to avoid file I/O on tab switches
        results = enterprise_data_service.get_cached_data('fap_results') or {}
        logger.debug(f"🏢 Retrieved FAP results from enterprise cache")
        return {"results": results, "data_source": "enterprise_cache"}
    except Exception as e:
        logger.error(f"Error getting enterprise FAP results: {str(e)}")
        # Fallback to standard service
        try:
            results = fap_results_service.load_fap_results()
            return {"results": results}
        except Exception as fallback_error:
            logger.error(f"FAP results fallback failed: {str(fallback_error)}")
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/fap/results/summary")
async def get_fap_results_summary():
    """Get FAP results summary"""
    try:
        summary = fap_results_service.get_results_summary()
        return summary
    except Exception as e:
        logger.error(f"Error getting FAP results summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/fap/results")
async def clear_fap_results():
    """Clear FAP results"""
    try:
        cleared = fap_results_service.clear_fap_results()
        return {"status": "success", "cleared": cleared}
    except Exception as e:
        logger.error(f"Error clearing FAP results: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/market/analysis/{symbol}/{period}")
async def get_market_analysis(symbol: str, period: str):
    """Get market analysis for symbol and period"""
    try:
        # Get historical data and perform analysis
        historical_data = await market_data_service.get_historical_data(symbol, period)
        
        # Create analysis using enterprise coordinator
        analysis_prompt = f"Analyze {symbol} market data for {period} period"
        analysis = await enterprise_coordinator.process_message(analysis_prompt, None)
        
        return {
            "symbol": symbol,
            "period": period,
            "analysis": analysis,
            "historical_data": historical_data
        }
    except Exception as e:
        logger.error(f"Error getting market analysis for {symbol}/{period}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/market-analysis/save")
async def save_market_analysis(request: dict):
    """Save market analysis"""
    try:
        analysis_data = {
            "symbol": request.get("symbol"),
            "period": request.get("period"),
            "analysis": request.get("analysis"),
            "timestamp": datetime.now().isoformat()
        }
        
        # Save using market analysis service
        market_analysis_service.save_analysis(
            request.get("symbol"),
            request.get("period"),
            request.get("analysis", "")
        )
        
        return {"status": "success", "message": "Market analysis saved"}
    except Exception as e:
        logger.error(f"Error saving market analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/market/data")
async def get_market_data():
    """Get complete market tab data in one call - Enterprise optimized with zero API calls"""
    try:
        logger.info("🏢 Loading market tab data from enterprise cache (zero API calls)...")
        
        # Get cached data
        market_analysis = enterprise_data_service.get_cached_data('market_analysis') or {}
        
        # If no cached market data, provide default indices data
        if not market_analysis or not market_analysis.get('indices'):
            default_indices = [
                {
                    "symbol": "SPY",
                    "name": "S&P 500 ETF",
                    "price": 450.25,
                    "change": 2.15,
                    "change_percent": 0.48
                },
                {
                    "symbol": "QQQ", 
                    "name": "NASDAQ ETF",
                    "price": 378.90,
                    "change": -1.45,
                    "change_percent": -0.38
                },
                {
                    "symbol": "IWM",
                    "name": "Russell 2000 ETF", 
                    "price": 194.75,
                    "change": 0.95,
                    "change_percent": 0.49
                },
                {
                    "symbol": "DIA",
                    "name": "Dow Jones ETF",
                    "price": 342.10,
                    "change": 1.20,
                    "change_percent": 0.35
                }
            ]
            
            market_analysis = {
                "indices": default_indices,
                "last_updated": "2025-06-25T15:00:00Z",
                "data_source": "enterprise_default"
            }
        
        return {
            "tab_type": "market_cached",
            "analysis": market_analysis,
            "cache_info": {
                "data_source": "enterprise_file_cache_only",
                "api_calls_made": 0
            }
        }
        
    except Exception as e:
        logger.error(f"Error loading enterprise market data: {str(e)}")
        return {
            "tab_type": "error",
            "error": str(e),
            "cache_info": {"data_source": "error", "api_calls_made": 0}
        }

@app.get("/api/v1/profile/portfolio/summary")
async def get_profile_portfolio_summary():
    """Get profile portfolio summary"""
    try:
        summary = profile_portfolio_service.get_portfolio_summary()
        return summary
    except Exception as e:
        logger.error(f"Error getting profile portfolio summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/v1/profile/portfolio/update")
async def update_profile_portfolio(request: dict):
    """Update profile portfolio"""
    try:
        updated_data = profile_portfolio_service.update_profile_portfolio(
            request.get("user_profile", {}),
            request.get("portfolio_allocation", []),
            request.get("portfolio_summary", "")
        )
        return updated_data
    except Exception as e:
        logger.error(f"Error updating profile portfolio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/profile/portfolio")
async def clear_profile_portfolio():
    """Clear profile portfolio"""
    try:
        cleared = profile_portfolio_service.clear_profile_portfolio()
        return {"status": "success", "cleared": cleared}
    except Exception as e:
        logger.error(f"Error clearing profile portfolio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/fap/results/session")
async def update_fap_session_status(request: dict):
    """Update FAP session status"""
    try:
        session_id = request.get("session_id")
        status = request.get("status", "active")
        # Update session status - convert string to boolean
        active_status = status.lower() == "active"
        fap_results_service.update_session_status(active_status)
        return {"status": "success", "message": "Session status updated"}
    except Exception as e:
        logger.error(f"Error updating FAP session status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/profile/portfolio")
async def get_profile_portfolio():
    """Get profile portfolio - Enterprise optimized from cache"""
    try:
        # Use cached data to avoid file I/O on tab switches
        portfolio_data = enterprise_data_service.get_cached_data('profile_portfolio') or {}
        logger.debug(f"🏢 Retrieved profile portfolio from enterprise cache")
        return portfolio_data if portfolio_data else {"error": "No profile portfolio found"}
    except Exception as e:
        logger.error(f"Error getting enterprise profile portfolio: {str(e)}")
        # Fallback to standard service
        try:
            portfolio = profile_portfolio_service.load_profile_portfolio()
            return portfolio if portfolio else {"error": "No profile portfolio found"}
        except Exception as fallback_error:
            logger.error(f"Profile portfolio fallback failed: {str(fallback_error)}")
            raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/profile/portfolio/save")
async def save_profile_portfolio(request: dict):
    """Save profile portfolio - Enterprise optimized with cache update"""
    try:
        required_fields = ["user_profile", "portfolio_allocation", "portfolio_summary"]
        for field in required_fields:
            if field not in request:
                raise ValueError(f"Missing required field: {field}")
        
        saved_data = profile_portfolio_service.save_profile_portfolio(
            request["user_profile"],
            request["portfolio_allocation"], 
            request["portfolio_summary"]
        )
        
        # Update enterprise cache with new data
        enterprise_data_service.update_cache_data('profile_portfolio', saved_data)
        logger.info("🏢 Enterprise cache updated after profile portfolio save")
        
        return saved_data
    except Exception as e:
        logger.error(f"Error saving enterprise profile portfolio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/profile/portfolio/allocation/{risk_tolerance}")
async def get_allocation_by_risk_profile(risk_tolerance: str):
    """Get allocation by risk profile"""
    try:
        allocation = profile_portfolio_service.get_allocation_by_risk_profile(risk_tolerance)
        return {"allocation": allocation, "risk_tolerance": risk_tolerance}
    except Exception as e:
        logger.error(f"Error getting allocation for {risk_tolerance}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/profile", response_model=UserProfileResponse)
async def create_profile(request: UserProfileRequest):
    """Create a new user profile with enterprise features"""
    try:
        user_id = str(uuid.uuid4())
        profile = user_profile_service.create_default_profile(
            user_id=user_id,
            name=request.name,
            age=request.age,
            income=request.income
        )
        
        # Update profile with user preferences
        profile.risk_tolerance = request.risk_tolerance
        profile.investment_goal = request.investment_goal
        profile.investment_horizon = request.investment_horizon
        
        if not user_profile_service.save_profile(profile):
            raise HTTPException(status_code=500, detail="Failed to save profile")
        
        # Refresh enterprise cache after profile creation
        enterprise_data_service.invalidate_cache()
        logger.info("🏢 Enterprise cache refreshed after profile creation")
        
        return UserProfileResponse(
            user_id=profile.user_id,
            name=profile.name,
            risk_tolerance=profile.risk_tolerance,
            investment_goal=profile.investment_goal,
            investment_horizon=profile.investment_horizon,
            preferences=[p.model_dump() for p in profile.preferences]
        )
    except Exception as e:
        logger.error(f"Error creating user profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

class InvestmentProposalResponse(BaseModel):
    user_id: str
    proposal: str

@app.put("/api/v1/profile/{user_id}")
async def update_profile(user_id: str = Path(...), request: UserProfileRequest = None):
    """Update an existing user profile with enterprise analysis"""
    try:
        # Load and update the profile
        profile = user_profile_service.load_profile()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Update profile fields
        profile.name = request.name
        profile.age = request.age
        profile.income = request.income
        profile.risk_tolerance = request.risk_tolerance
        profile.investment_goal = request.investment_goal
        profile.investment_horizon = request.investment_horizon
        
        # Save updated profile
        user_profile_service.save_profile(profile)
        
        # Use enterprise coordinator for enhanced analysis
        user_profile_dict = {
            "age": profile.age,
            "risk_tolerance": profile.risk_tolerance,
            "investment_goal": profile.investment_goal,
            "investment_horizon": profile.investment_horizon,
            "name": profile.name,
            "income": profile.income
        }
        
        # Generate enhanced report using enterprise features
        response = await enterprise_coordinator.process_message(
            f"Generate investment recommendations for {profile.name}, age {profile.age}, {profile.risk_tolerance} risk tolerance, ${profile.income} income, goal: {profile.investment_goal}",
            None
        )
        
        # Generate allocation based on risk tolerance
        def get_allocation_for_risk_tolerance(risk_tolerance):
            """Get allocation based on risk tolerance"""
            risk_tolerance = risk_tolerance.lower()
            if risk_tolerance == 'conservative':
                return [
                    {"asset_type": "bonds", "allocation_percentage": 70},
                    {"asset_type": "stocks", "allocation_percentage": 20},
                    {"asset_type": "cash", "allocation_percentage": 10}
                ]
            elif risk_tolerance == 'moderate':
                return [
                    {"asset_type": "stocks", "allocation_percentage": 50},
                    {"asset_type": "bonds", "allocation_percentage": 30},
                    {"asset_type": "cash", "allocation_percentage": 15},
                    {"asset_type": "real_estate", "allocation_percentage": 5}
                ]
            else:  # aggressive
                return [
                    {"asset_type": "stocks", "allocation_percentage": 70},
                    {"asset_type": "bonds", "allocation_percentage": 15},
                    {"asset_type": "real_estate", "allocation_percentage": 10},
                    {"asset_type": "cash", "allocation_percentage": 5}
                ]
        
        # Also update the profile portfolio storage with new data
        allocation = get_allocation_for_risk_tolerance(profile.risk_tolerance)
        
        profile_portfolio_service.update_profile_portfolio(
            user_profile=user_profile_dict,
            portfolio_allocation=allocation,
            portfolio_summary=response
        )
        
        # Refresh enterprise cache after profile and portfolio update
        enterprise_data_service.invalidate_cache()
        logger.info(f"🏢 Profile and portfolio data updated for user {profile.name} (Enterprise Mode) - Cache refreshed")
        
        return InvestmentProposalResponse(user_id=profile.user_id, proposal=response)
        
    except Exception as e:
        logger.error(f"Error updating user profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/fap/analyze")
async def fap_analyze(request: dict):
    """Financial Analysis Pipeline with enterprise features"""
    try:
        # Extract user profile data
        user_profile = {
            "name": request.get("name", ""),
            "age": request.get("age", 0),
            "income": request.get("income", 0),
            "risk_tolerance": request.get("risk_tolerance", "moderate"),
            "investment_goal": request.get("investment_goal", "growth"),
            "investment_horizon": request.get("investment_horizon", "long-term")
        }
        
        # Use enterprise coordinator for enhanced FAP analysis
        analysis_prompt = f"""
        Perform comprehensive financial analysis for:
        - Name: {user_profile['name']}
        - Age: {user_profile['age']}
        - Income: ${user_profile['income']:,}
        - Risk Tolerance: {user_profile['risk_tolerance']}
        - Investment Goal: {user_profile['investment_goal']}
        - Investment Horizon: {user_profile['investment_horizon']}
        
        Provide detailed portfolio recommendations with specific allocations.
        """
        
        response = await enterprise_coordinator.process_message(analysis_prompt, None)
        
        # Extract allocation from AI analysis text
        def extract_allocation_from_analysis(analysis_text):
            """Extract portfolio allocation percentages from AI analysis text"""
            import re
            
            allocation = []
            
            # Look for patterns like "Stocks (20% of Portfolio)" or "Bonds (70%)"
            patterns = [
                (r"Stocks?\s*\((\d+)%", "stocks"),
                (r"Bonds?\s*\((\d+)%", "bonds"),
                (r"Cash.*?\((\d+)%", "cash"),
                (r"Real Estate.*?\((\d+)%", "real_estate"),
                (r"ETFs?\s*\((\d+)%", "etfs"),
                (r"REITs?\s*\((\d+)%", "reits"),
                (r"Commodities.*?\((\d+)%", "commodities"),
                (r"Cryptocurrency.*?\((\d+)%", "cryptocurrency")
            ]
            
            for pattern, asset_type in patterns:
                matches = re.findall(pattern, analysis_text, re.IGNORECASE)
                if matches:
                    percentage = int(matches[0])
                    allocation.append({
                        "asset_type": asset_type,
                        "allocation_percentage": percentage
                    })
            
            # If no allocation found in text, use conservative defaults based on risk tolerance
            if not allocation:
                risk_tolerance = user_profile.get('risk_tolerance', 'moderate').lower()
                if risk_tolerance == 'conservative':
                    allocation = [
                        {"asset_type": "bonds", "allocation_percentage": 70},
                        {"asset_type": "stocks", "allocation_percentage": 20},
                        {"asset_type": "cash", "allocation_percentage": 10}
                    ]
                elif risk_tolerance == 'moderate':
                    allocation = [
                        {"asset_type": "stocks", "allocation_percentage": 50},
                        {"asset_type": "bonds", "allocation_percentage": 30},
                        {"asset_type": "cash", "allocation_percentage": 15},
                        {"asset_type": "real_estate", "allocation_percentage": 5}
                    ]
                else:  # aggressive
                    allocation = [
                        {"asset_type": "stocks", "allocation_percentage": 70},
                        {"asset_type": "bonds", "allocation_percentage": 15},
                        {"asset_type": "real_estate", "allocation_percentage": 10},
                        {"asset_type": "cash", "allocation_percentage": 5}
                    ]
            
            return allocation
        
        extracted_allocation = extract_allocation_from_analysis(response)
        
        # Create FAP context response
        fap_context = {
            "user_profile": user_profile,
            "analysis_result": response,
            "allocation": extracted_allocation,
            "risk_assessment": f"Risk level: {user_profile['risk_tolerance']}",
            "session_id": request.get("session_id", str(uuid.uuid4())),
            "timestamp": datetime.now().isoformat()
        }
        
        # Save FAP results
        fap_results_service.save_fap_results(fap_context)
        
        return {"fap_context": fap_context, "used_fallback": False}
        
    except Exception as e:
        logger.error(f"Error in FAP analyze: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/portfolio/analysis")
async def get_portfolio_analysis():
    """Return dynamically generated allocation and report based on current user profile - Enterprise optimized"""
    try:
        # Use enterprise data service for cached profile data
        logger.info("🏢 Loading portfolio analysis from enterprise cache...")
        user_profile_data = enterprise_data_service.get_cached_data('user_profile')
        
        if not user_profile_data or not user_profile_data.get('name'):
            return JSONResponse(status_code=404, content={"error": "No user profile found"})
        
        # Use enterprise coordinator for enhanced analysis with real profile data
        user_profile_dict = {
            "age": user_profile_data.get("age", 35),
            "risk_tolerance": user_profile_data.get("risk_tolerance", "moderate"),
            "investment_goal": user_profile_data.get("investment_goal", "long-term growth"),
            "investment_horizon": user_profile_data.get("investment_horizon", "long-term"),
            "name": user_profile_data.get("name", "User"),
            "income": user_profile_data.get("income", 75000)
        }
        
        logger.info(f"🏢 Generating analysis for {user_profile_dict['name']}, age {user_profile_dict['age']}, income ${user_profile_dict['income']}")
        
        # Generate comprehensive report using enterprise features with real data
        response = await enterprise_coordinator.process_message(
            f"Generate a comprehensive portfolio analysis for {user_profile_dict['name']}, age {user_profile_dict['age']}, income ${user_profile_dict['income']}, {user_profile_dict['risk_tolerance']} risk tolerance, goal: {user_profile_dict['investment_goal']}, horizon: {user_profile_dict['investment_horizon']}",
            None
        )
        
        # Extract allocation from analysis or use risk-based defaults
        def get_allocation_for_risk_tolerance(risk_tolerance):
            """Get allocation based on risk tolerance"""
            risk_tolerance = risk_tolerance.lower()
            if risk_tolerance == 'conservative':
                return [
                    {"asset_type": "bonds", "allocation_percentage": 70},
                    {"asset_type": "stocks", "allocation_percentage": 20},
                    {"asset_type": "cash", "allocation_percentage": 10}
                ]
            elif risk_tolerance == 'moderate':
                return [
                    {"asset_type": "stocks", "allocation_percentage": 50},
                    {"asset_type": "bonds", "allocation_percentage": 30},
                    {"asset_type": "cash", "allocation_percentage": 15},
                    {"asset_type": "real_estate", "allocation_percentage": 5}
                ]
            else:  # aggressive
                return [
                    {"asset_type": "stocks", "allocation_percentage": 70},
                    {"asset_type": "bonds", "allocation_percentage": 15},
                    {"asset_type": "real_estate", "allocation_percentage": 10},
                    {"asset_type": "cash", "allocation_percentage": 5}
                ]
        
        allocation = get_allocation_for_risk_tolerance(user_profile_dict['risk_tolerance'])
        
        return {
            "allocation": allocation,
            "report": response,
            "data_source": "enterprise_cache"
        }
        
    except Exception as e:
        logger.error(f"Error loading enterprise portfolio analysis: {str(e)}")
        # Fallback to standard service
        try:
            profile = user_profile_service.load_profile()
            if not profile:
                return JSONResponse(status_code=404, content={"error": "No user profile found"})
            
            response = await enterprise_coordinator.process_message(
                f"Generate a portfolio analysis for {profile.name} with {profile.risk_tolerance} risk tolerance",
                None
            )
            
            # Use risk-based allocation for fallback as well
            fallback_allocation = get_allocation_for_risk_tolerance(profile.risk_tolerance)
            
            return {
                "allocation": fallback_allocation,
                "report": response,
                "data_source": "fallback_service"
            }
        except Exception as fallback_error:
            logger.error(f"Portfolio analysis fallback failed: {str(fallback_error)}")
            return JSONResponse(status_code=500, content={"error": str(e)})

# Legacy endpoint compatibility
@app.post("/api/v1/chat", response_model=ChatResponse)
async def legacy_chat(request: ChatRequest):
    """Legacy chat endpoint for backward compatibility"""
    try:
        # Use enterprise coordinator but return simple response
        response = await enterprise_coordinator.process_message(request.message, request.user_id)
        return ChatResponse(response=response)
    except Exception as e:
        logger.error(f"Error in legacy chat: {str(e)}")
        return ChatResponse(response="I apologize for the technical difficulty.", error=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)