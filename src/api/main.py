"""
FastAPI application for Financial Investment Advisor Agent System
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
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
coordinator = CoordinatorAgent(user_profile_service=user_profile_service)
market_data_service = MarketDataService()

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
    return {"status": "healthy"}

@app.put("/api/v1/profile/{user_id}", response_model=InvestmentProposalResponse)
async def update_profile(user_id: str = Path(...), request: UserProfileRequest = None):
    """Update an existing user profile and return investment proposal"""
    try:
        # Load and update the profile
        profile = user_profile_service.load_profile()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        profile.name = request.name
        profile.age = request.age
        profile.income = request.income
        profile.risk_tolerance = request.risk_tolerance
        profile.investment_goal = request.investment_goal
        profile.investment_horizon = request.investment_horizon
        # Use multi-agent system to generate new allocation
        portfolio_response = await coordinator.process_message(
            f"User profile updated: Name: {profile.name}, Age: {profile.age}, Income: {profile.income}, Risk Tolerance: {profile.risk_tolerance}, Investment Goal: {profile.investment_goal}, Investment Horizon: {profile.investment_horizon}. Please propose a personalized investment option with recommended portfolio allocation only as a list (e.g., Stocks: 50%, Bonds: 20%, Cash: 5%, Real Estate: 10%, Commodities: 5%, Cryptocurrency: 3%, ETFs: 5%, REITs: 2%). Include all asset classes, even if the allocation is 0%. In your report, clearly label sections as 'Summary', 'Market Outlook', and 'Recommendations', and ensure the allocation in the report matches the recommended allocation list. Format your output as:\n---\nPortfolio Allocation:\n<list>\n---\nReport:\nSummary:\n<summary>\nMarket Outlook:\n<outlook>\nRecommendations:\n<recommendations>\n---",
            profile.user_id
        )
        # Parse allocation and report
        alloc_match = re.search(r"Portfolio Allocation:\n([\s\S]*?)---", portfolio_response)
        report_match = re.search(r"Report:\n([\s\S]*?)---", portfolio_response)
        allocation_lines = alloc_match.group(1).strip().split("\n") if alloc_match else []
        allocation = []
        for line in allocation_lines:
            m = re.match(r"-?\s*([A-Za-z ]+):\s*(\d+(?:\.\d+)?)%", line)
            if m:
                allocation.append({
                    "asset_type": m.group(1).strip().lower(),
                    "allocation_percentage": float(m.group(2))
                })
        # If report section is missing, use the whole output as the report
        if report_match:
            report = report_match.group(1).strip()
        else:
            report = portfolio_response.strip()
        # Save the latest report to the profile and persist
        profile.last_report = report
        user_profile_service.save_profile(profile)
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
    if request.fallback:
        # Use the old agent pipeline as fallback
        coordinator = CoordinatorAgent()
        profile_str = f"Name: {request.name}, Age: {request.age}, Income: {request.income}, Risk Tolerance: {request.risk_tolerance}, Investment Goal: {request.investment_goal}, Investment Horizon: {request.investment_horizon}"
        response = await coordinator.process_message(profile_str)
        return FAPAnalyzeResponse(fap_context={}, used_fallback=True, fallback_response=response)
    
    # Build FAP context
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
        quote = await market_data_service.get_market_data([symbol])
        if not quote or symbol not in quote:
            raise HTTPException(status_code=404, detail="Symbol not found or API error")
        return quote[symbol]
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

@app.get("/api/v1/profile")
async def get_profile():
    """Get complete user profile"""
    try:
        profile = user_profile_service.load_profile()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        return {
            "user_id": profile.user_id,
            "name": profile.name,
            "age": profile.age,
            "income": profile.income,
            "risk_tolerance": profile.risk_tolerance,
            "investment_goal": profile.investment_goal,
            "investment_horizon": profile.investment_horizon,
            "created_at": profile.created_at.isoformat() if profile.created_at else None,
            "updated_at": profile.updated_at.isoformat() if profile.updated_at else None
        }
    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 