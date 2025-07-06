"""
FastAPI application for Financial Investment Advisor Agent System
"""

from fastapi import FastAPI, HTTPException
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

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Financial Investment Advisor API",
    description="API for the Financial Investment Advisor Agent System",
    version="1.0.0"
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
coordinator = CoordinatorAgent(user_profile_service=user_profile_service)

# Define request/response models
class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None

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

class InvestmentProposalResponse(BaseModel):
    user_id: str
    proposal: str

class FAPAnalyzeRequest(BaseModel):
    """Request model for Financial Analysis Pipeline"""
    name: str
    age: int
    income: float
    risk_tolerance: str
    investment_goal: str
    investment_horizon: str
    session_id: Optional[str] = None
    fallback: Optional[bool] = False
    additional_context: Optional[Dict[str, Any]] = None

class FAPAnalyzeResponse(BaseModel):
    """Response model for Financial Analysis Pipeline"""
    fap_context: Dict
    used_fallback: bool = False
    fallback_response: Optional[str] = None

# Define routes
@app.post("/api/v1/chat", response_model=ChatResponse)
async def process_chat(request: ChatRequest):
    """Process chat messages and return responses"""
    try:
        response = await coordinator.process_message(request.message, request.user_id)
        return ChatResponse(response=response)
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/profile", response_model=UserProfileResponse)
async def create_profile(request: UserProfileRequest):
    """Create a new user profile"""
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

@app.get("/api/v1/portfolio/summary")
async def get_portfolio_summary():
    """Get user's portfolio summary or signal no profile exists"""
    try:
        summary = user_profile_service.get_portfolio_summary()
        if "error" in summary and summary["error"] == "No user profile found":
            return {"no_profile": True}
        if "error" in summary:
            raise HTTPException(status_code=404, detail=summary["error"])
        return summary
    except Exception as e:
        logger.error(f"Error getting portfolio summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "mode": "standard", "features": ["basic_portfolio", "market_data", "user_profiles"]}

@app.get("/api/v1/backend/mode")
async def get_backend_mode():
    """Get backend mode information"""
    return {
        "mode": "standard",
        "version": "1.0.0",
        "features": {
            "enterprise_chat": False,
            "plugin_manager": False,
            "responsible_ai": False,
            "compliance_checking": False,
            "advanced_analytics": False
        },
        "description": "Standard Financial Investment Advisor"
    }

@app.put("/api/v1/profile/{user_id}", response_model=InvestmentProposalResponse)
async def update_profile(user_id: str = Path(...), request: UserProfileRequest = None):
    """Update an existing user profile and return investment proposal"""
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
        
        # Save updated profile BEFORE generating allocation to ensure coordinator uses latest data
        user_profile_service.save_profile(profile)
        
        # Generate new allocation using coordinator agent
        coordinator = CoordinatorAgent(user_profile_service=user_profile_service)
        user_profile_dict = {
            "age": profile.age,
            "risk_tolerance": profile.risk_tolerance,
            "investment_goal": profile.investment_goal,
            "investment_horizon": profile.investment_horizon,
            "name": profile.name,
            "income": profile.income
        }
        
        # Generate comprehensive report with synchronized data
        report_data = await coordinator.generate_comprehensive_report(user_profile_dict)
        
        # Update profile preferences to match the new allocation
        if report_data["allocation"]:
            # Clear existing preferences and add new ones
            profile.preferences = []
            for alloc in report_data["allocation"]:
                from ..models.user_profile import InvestmentPreference
                preference = InvestmentPreference(
                    asset_type=alloc["asset_type"],
                    allocation_percentage=alloc["allocation_percentage"],
                    risk_tolerance=profile.risk_tolerance,
                    is_active=True
                )
                profile.preferences.append(preference)
            
            # Save updated profile with new report
            profile.last_report = report_data["report"]
            user_profile_service.save_profile(profile)
            
            # Also update the profile portfolio storage with new data
            profile_portfolio_service.update_profile_portfolio(
                user_profile={
                    "name": profile.name,
                    "age": profile.age,
                    "income": profile.income,
                    "risk_tolerance": profile.risk_tolerance,
                    "investment_goal": profile.investment_goal,
                    "investment_horizon": profile.investment_horizon
                },
                portfolio_allocation=report_data["allocation"],
                portfolio_summary=report_data["report"]
            )
            
            logger.info(f"Profile and portfolio data updated for user {profile.name}")
        
        # Format the response as investment proposal
        portfolio_response = f"""---
Portfolio Allocation:
{chr(10).join([f"- {alloc['asset_type'].replace('_', ' ').title()}: {alloc['allocation_percentage']}%" for alloc in report_data["allocation"]])}
---
Report:
{report_data["report"]}
---"""
        
        return InvestmentProposalResponse(user_id=profile.user_id, proposal=portfolio_response)
        
    except Exception as e:
        logger.error(f"Error updating user profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/portfolio/analysis")
async def get_portfolio_analysis():
    """Return dynamically generated allocation and report based on current user profile."""
    try:
        profile = user_profile_service.load_profile()
        if not profile:
            return JSONResponse(status_code=404, content={"error": "No user profile found"})
        
        # Generate dynamic allocation and report using the coordinator agent
        coordinator = CoordinatorAgent(user_profile_service=user_profile_service)
        user_profile_dict = {
            "age": profile.age,
            "risk_tolerance": profile.risk_tolerance,
            "investment_goal": profile.investment_goal,
            "investment_horizon": profile.investment_horizon,
            "name": profile.name,
            "income": profile.income
        }
        
        # Generate comprehensive report with synchronized data
        report_data = await coordinator.generate_comprehensive_report(user_profile_dict)
        
        # Update profile preferences to match the new allocation
        if report_data["allocation"]:
            # Clear existing preferences and add new ones
            profile.preferences = []
            for alloc in report_data["allocation"]:
                from ..models.user_profile import InvestmentPreference
                preference = InvestmentPreference(
                    asset_type=alloc["asset_type"],
                    allocation_percentage=alloc["allocation_percentage"],
                    risk_tolerance=profile.risk_tolerance,
                    is_active=True
                )
                profile.preferences.append(preference)
            
            # Save updated profile with new report
            profile.last_report = report_data["report"]
            user_profile_service.save_profile(profile)
        
        return {
            "allocation": report_data["allocation"],
            "report": report_data["report"]
        }
        
    except Exception as e:
        logger.error(f"Error loading portfolio analysis: {str(e)}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/v1/fap/analyze", response_model=FAPAnalyzeResponse)
async def fap_analyze(request: FAPAnalyzeRequest):
    """
    Run the Financial Analysis Pipeline (FAP) or fallback to the old agent pipeline.
    
    This endpoint processes a complete financial analysis through 4 sequential steps:
    1. Risk Assessment
    2. Market Analysis  
    3. Portfolio Generation
    4. Report Generation
    """
    # Handle special cases with additional context
    if request.additional_context:
        analysis_type = request.additional_context.get("analysis_type")
        
        if analysis_type == "market_analysis":
            # Handle market analysis specifically
            coordinator = CoordinatorAgent()
            market_data = request.additional_context.get("market_data", {})
            period_analysis = market_data.get("period_analysis")
            
            # Create a focused market analysis prompt with period-specific data
            if period_analysis:
                # Use period-based analysis when available
                prompt = f"""
                You are a professional financial advisor. Provide a comprehensive market analysis for {market_data.get('name', 'the selected index')} ({market_data.get('symbol', 'N/A')}) with clear, actionable recommendations.
                
                CURRENT MARKET DATA:
                - Current Price: ${market_data.get('current_price', 'N/A')}
                - Daily Change: ${market_data.get('daily_change', 'N/A')} ({market_data.get('daily_change_percent', 'N/A')}%)
                
                PERIOD ANALYSIS ({period_analysis['period']} timeframe):
                - Start Price: ${period_analysis['start_price']:.2f}
                - End Price: ${period_analysis['end_price']:.2f}
                - Total Change: ${period_analysis['period_change']:.2f} ({period_analysis['period_change_percent']:.2f}%)
                - Period High: ${period_analysis['high_price']:.2f}
                - Period Low: ${period_analysis['low_price']:.2f}
                - Volatility: {period_analysis['volatility']:.1f}% (annualized)
                
                USER PROFILE:
                - Risk Tolerance: {request.risk_tolerance}
                - Investment Goal: {request.investment_goal}
                - Investment Horizon: {request.investment_horizon}
                
                Please structure your response with these exact sections:
                
                📈 MARKET TREND ANALYSIS ({period_analysis['period']} Performance):
                [Analyze the {period_analysis['period_change']:.2f} change over {period_analysis['period']} period, trend direction, momentum]
                
                📊 TECHNICAL ANALYSIS:
                [Support/resistance levels based on period high ${period_analysis['high_price']:.2f} and low ${period_analysis['low_price']:.2f}, key price levels]
                
                ⚠️ RISK ASSESSMENT:
                [Volatility analysis based on {period_analysis['volatility']:.1f}% volatility, risk factors, correlation with market]
                
                💰 FINANCIAL ADVISOR RECOMMENDATIONS:
                [Specific actionable advice based on {request.risk_tolerance} risk tolerance and {request.investment_goal} goal]
                
                🎯 PORTFOLIO ALLOCATION GUIDANCE:
                [Suggested allocation percentage for this asset in a {request.risk_tolerance} risk portfolio]
                
                ⏰ TIMING & ENTRY STRATEGY:
                [Best entry points, dollar-cost averaging suggestions, timing considerations]
                
                🚨 KEY LEVELS TO WATCH:
                [Critical support/resistance levels, stop-loss suggestions, profit-taking levels]
                
                Keep each section concise but actionable. Focus on practical investment decisions.
                """
            else:
                # Fallback to basic analysis when period data is not available
                prompt = f"""
                You are a professional financial advisor. Provide a market analysis for {market_data.get('name', 'the selected index')} ({market_data.get('symbol', 'N/A')}).
                
                CURRENT MARKET DATA:
                - Current Price: ${market_data.get('current_price', 'N/A')}
                - Daily Change: {market_data.get('daily_change', 'N/A')} ({market_data.get('daily_change_percent', 'N/A')}%)
                - Selected Period: {market_data.get('period', '1d')}
                
                USER PROFILE:
                - Risk Tolerance: {request.risk_tolerance}
                - Investment Goal: {request.investment_goal}
                - Investment Horizon: {request.investment_horizon}
                
                Please provide structured analysis with clear recommendations based on the user's {request.risk_tolerance} risk tolerance and {request.investment_goal} investment goal.
                """
            
            response = await coordinator.process_message(prompt)
            return FAPAnalyzeResponse(
                fap_context={"report": response}, 
                used_fallback=True, 
                fallback_response=response
            )
        
        elif analysis_type == "journal_insights":
            # Handle journal insights
            coordinator = CoordinatorAgent()
            journal_entry = request.additional_context.get("journal_entry", "")
            symbol = request.additional_context.get("symbol", "")
            
            prompt = f"""
            Analyze this investment journal entry and provide insights:
            
            Journal Entry: "{journal_entry}"
            {f"Related Symbol: {symbol}" if symbol else ""}
            
            User Profile:
            - Risk Tolerance: {request.risk_tolerance}
            - Investment Goal: {request.investment_goal}
            - Investment Horizon: {request.investment_horizon}
            
            Please provide:
            1. Analysis of the investment thoughts/decisions mentioned
            2. Potential risks or opportunities identified
            3. Recommendations based on the user's risk profile
            4. Educational insights related to the content
            
            Keep the response concise but insightful.
            """
            
            response = await coordinator.process_message(prompt)
            return FAPAnalyzeResponse(
                fap_context={"report": response}, 
                used_fallback=True, 
                fallback_response=response
            )
    
    if request.fallback:
        # Use the old agent pipeline as fallback
        coordinator = CoordinatorAgent()
        profile_str = f"Name: {request.name}, Age: {request.age}, Income: {request.income}, Risk Tolerance: {request.risk_tolerance}, Investment Goal: {request.investment_goal}, Investment Horizon: {request.investment_horizon}"
        response = await coordinator.process_message(profile_str)
        return FAPAnalyzeResponse(fap_context={}, used_fallback=True, fallback_response=response)
    
    # Build FAP context for normal pipeline
    context = FAPContext(
        user_profile={
            "name": request.name,
            "age": request.age,
            "income": request.income,
            "risk_tolerance": request.risk_tolerance,
            "investment_goal": request.investment_goal,
            "investment_horizon": request.investment_horizon,
        },
        session_id=request.session_id or str(uuid.uuid4()),
        history=[]
    )
    
    # Execute the Financial Analysis Pipeline
    context = await run_fap_pipeline(context)
    
    # Save FAP results automatically
    try:
        user_profile_data = {
            "name": request.name,
            "age": request.age,
            "income": request.income,
            "risk_tolerance": request.risk_tolerance,
            "investment_goal": request.investment_goal,
            "investment_horizon": request.investment_horizon
        }
        fap_results_service.save_fap_results(context.model_dump(), user_profile_data)
    except Exception as e:
        logger.warning(f"Failed to save FAP results: {str(e)}")
    
    return FAPAnalyzeResponse(fap_context=context.model_dump(), used_fallback=False)

@app.get("/api/v1/portfolio/holdings")
async def get_portfolio_holdings():
    """Get all portfolio holdings"""
    try:
        return portfolio_service.get_holdings()
    except Exception as e:
        logger.error(f"Error getting portfolio holdings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/portfolio/holdings")
async def add_portfolio_holding(holding: PortfolioHolding):
    """Add a new holding to the portfolio"""
    try:
        portfolio_service.add_holding(holding)
        # Also record a transaction for this new holding
        transaction = portfolio_service.add_transaction(holding)
        return {"holding": holding, "transaction": transaction}
    except Exception as e:
        logger.error(f"Error adding portfolio holding: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/portfolio/transactions")
async def get_transactions():
    """Get all transactions"""
    try:
        return portfolio_service.get_transactions()
    except Exception as e:
        logger.error(f"Error getting transactions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/journal")
async def get_journal_entries():
    """Get all journal entries"""
    try:
        return journal_service.get_entries()
    except Exception as e:
        logger.error(f"Error getting journal entries: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/journal")
async def add_journal_entry(entry: JournalEntry):
    """Add a new entry to the journal"""
    try:
        new_entry = journal_service.add_entry(entry)
        return new_entry
    except Exception as e:
        logger.error(f"Error adding journal entry: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/market/quote/{symbol}")
async def get_market_quote(symbol: str):
    """Get a real-time quote for a given stock symbol"""
    try:
        # Use get_stock_data for comprehensive stock information
        quote_data = await market_data_service.get_stock_data(symbol)
        
        # Check for API errors
        if "error" in quote_data:
            raise HTTPException(status_code=400, detail=quote_data["error"])
        
        # Ensure symbol is always included in response for frontend validation
        quote_data["symbol"] = symbol.upper()
        
        return quote_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting market quote for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/market/indices")
async def get_market_indices():
    """Get a list of major market indices."""
    try:
        indices = await market_data_service.get_major_indices()
        return indices
    except Exception as e:
        logger.error(f"Error getting market indices: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/market/historical/{symbol}")
async def get_historical_market_data(symbol: str, period: str = "1d"):
    """Get historical data for a given symbol and period."""
    try:
        historical_data = await market_data_service.get_historical_data(symbol, period)
        if "error" in historical_data:
            raise HTTPException(status_code=404, detail=historical_data["error"])
        return historical_data
    except Exception as e:
        logger.error(f"Error getting historical data for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v2/portfolio/analysis")
async def get_portfolio_analysis():
    """Endpoint to analyze portfolio"""
    try:
        profile = user_profile_service.load_profile()
        if not profile:
            return JSONResponse(status_code=404, content={"error": "No user profile found"})
        # Build allocation from saved preferences
        allocation = [
            {
                "asset_type": pref.asset_type,
                "allocation_percentage": pref.allocation_percentage
            }
            for pref in profile.preferences if pref.is_active
        ]
        report = profile.last_report or "No report available."
        return {"allocation": allocation, "report": report}
    except Exception as e:
        logger.error(f"Error loading portfolio analysis: {str(e)}")
        return JSONResponse(status_code=500, content={"error": str(e)})

# Market Analysis Storage Endpoints
@app.post("/api/v1/market-analysis/save")
async def save_market_analysis(request: dict):
    """Save market analysis to local storage"""
    try:
        symbol = request.get('symbol')
        period = request.get('period')
        analysis = request.get('analysis')
        market_data = request.get('market_data', {})
        user_profile = request.get('user_profile', {})
        
        if not all([symbol, period, analysis]):
            raise HTTPException(status_code=400, detail="Missing required fields: symbol, period, analysis")
        
        result = market_analysis_service.save_analysis(symbol, period, analysis, market_data, user_profile)
        return {"success": True, "analysis": result}
        
    except Exception as e:
        logger.error(f"Error saving market analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/market/analysis/{symbol}/{period}")
async def get_market_analysis(symbol: str, period: str):
    """Get saved market analysis for specific symbol and period"""
    try:
        analysis = market_analysis_service.load_analysis(symbol, period)
        if analysis:
            return {"success": True, "analysis": analysis}
        else:
            return {"success": False, "message": "Analysis not found"}
            
    except Exception as e:
        logger.error(f"Error loading market analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/market/analysis/recent")
async def get_recent_market_analyses(limit: int = 10):
    """Get recent market analyses"""
    try:
        analyses = market_analysis_service.get_recent_analyses(limit)
        return {"success": True, "analyses": analyses}
        
    except Exception as e:
        logger.error(f"Error getting recent analyses: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/market/analysis/summary")
async def get_market_analysis_summary():
    """Get summary of stored market analyses"""
    try:
        summary = market_analysis_service.get_analysis_summary()
        return {"success": True, "summary": summary}
        
    except Exception as e:
        logger.error(f"Error getting analysis summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/market/analysis/{symbol}/{period}")
async def delete_market_analysis(symbol: str, period: str):
    """Delete specific market analysis"""
    try:
        success = market_analysis_service.delete_analysis(symbol, period)
        if success:
            return {"success": True, "message": "Analysis deleted successfully"}
        else:
            return {"success": False, "message": "Analysis not found"}
            
    except Exception as e:
        logger.error(f"Error deleting market analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# FAP Results Storage Endpoints
@app.get("/api/v1/fap/results")
async def get_fap_results():
    """Get saved FAP results"""
    try:
        results = fap_results_service.load_fap_results()
        if results:
            return {"success": True, "results": results}
        else:
            return {"success": False, "message": "No FAP results found"}
            
    except Exception as e:
        logger.error(f"Error loading FAP results: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/fap/results/summary")
async def get_fap_results_summary():
    """Get summary of stored FAP results"""
    try:
        summary = fap_results_service.get_results_summary()
        return {"success": True, "summary": summary}
        
    except Exception as e:
        logger.error(f"Error getting FAP results summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/fap/results")
async def clear_fap_results():
    """Clear stored FAP results"""
    try:
        success = fap_results_service.clear_fap_results()
        if success:
            return {"success": True, "message": "FAP results cleared successfully"}
        else:
            return {"success": False, "message": "No FAP results to clear"}
            
    except Exception as e:
        logger.error(f"Error clearing FAP results: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/fap/results/session")
async def update_fap_session_status(request: dict):
    """Update FAP session status"""
    try:
        active = request.get('active', True)
        success = fap_results_service.update_session_status(active)
        return {"success": success}
        
    except Exception as e:
        logger.error(f"Error updating FAP session status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Profile Portfolio Storage Endpoints
@app.get("/api/v1/profile/portfolio")
async def get_profile_portfolio():
    """Get saved profile portfolio"""
    try:
        portfolio = profile_portfolio_service.load_profile_portfolio()
        if portfolio:
            return {"success": True, "portfolio": portfolio}
        else:
            return {"success": False, "message": "No profile portfolio found"}
            
    except Exception as e:
        logger.error(f"Error loading profile portfolio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/profile/portfolio/save")
async def save_profile_portfolio(request: dict):
    """Save profile portfolio to local storage"""
    try:
        user_profile = request.get('user_profile')
        portfolio_allocation = request.get('portfolio_allocation')
        portfolio_summary = request.get('portfolio_summary')
        
        if not all([user_profile, portfolio_allocation, portfolio_summary]):
            raise HTTPException(status_code=400, detail="Missing required fields: user_profile, portfolio_allocation, portfolio_summary")
        
        result = profile_portfolio_service.save_profile_portfolio(user_profile, portfolio_allocation, portfolio_summary)
        return {"success": True, "portfolio": result}
        
    except Exception as e:
        logger.error(f"Error saving profile portfolio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/v1/profile/portfolio/update")
async def update_profile_portfolio(request: dict):
    """Update profile portfolio"""
    try:
        user_profile = request.get('user_profile')
        portfolio_allocation = request.get('portfolio_allocation')
        portfolio_summary = request.get('portfolio_summary')
        
        if not all([user_profile, portfolio_allocation, portfolio_summary]):
            raise HTTPException(status_code=400, detail="Missing required fields: user_profile, portfolio_allocation, portfolio_summary")
        
        result = profile_portfolio_service.update_profile_portfolio(user_profile, portfolio_allocation, portfolio_summary)
        return {"success": True, "portfolio": result}
        
    except Exception as e:
        logger.error(f"Error updating profile portfolio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/profile/portfolio")
async def clear_profile_portfolio():
    """Clear stored profile portfolio"""
    try:
        success = profile_portfolio_service.clear_profile_portfolio()
        if success:
            return {"success": True, "message": "Profile portfolio cleared successfully"}
        else:
            return {"success": False, "message": "No profile portfolio to clear"}
            
    except Exception as e:
        logger.error(f"Error clearing profile portfolio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/profile/portfolio/summary")
async def get_profile_portfolio_summary():
    """Get summary of stored profile portfolio"""
    try:
        summary = profile_portfolio_service.get_portfolio_summary()
        return {"success": True, "summary": summary}
        
    except Exception as e:
        logger.error(f"Error getting profile portfolio summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/profile/portfolio/allocation/{risk_tolerance}")
async def get_allocation_by_risk_profile(risk_tolerance: str):
    """Get default allocation based on risk profile"""
    try:
        allocation = profile_portfolio_service.get_allocation_by_risk_profile(risk_tolerance)
        return {"success": True, "allocation": allocation, "risk_tolerance": risk_tolerance}
        
    except Exception as e:
        logger.error(f"Error getting allocation by risk profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 