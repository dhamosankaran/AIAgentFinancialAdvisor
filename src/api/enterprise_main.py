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