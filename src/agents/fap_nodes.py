"""
Financial Analysis Pipeline (FAP) Nodes
Sequential processing nodes for comprehensive financial analysis workflow
"""
from src.models.fap_context import FAPContext
from src.agents.risk_assessment_agent import RiskAssessmentAgent
from src.agents.market_analysis_agent import MarketAnalysisAgent
from src.agents.portfolio_agent import PortfolioAgent
import copy

# Initialize specialized agents
risk_agent = RiskAssessmentAgent()
market_agent = MarketAnalysisAgent()
portfolio_agent = PortfolioAgent()

async def risk_assessment_node(context: FAPContext) -> FAPContext:
    """
    Step 1: Risk Assessment Node
    Analyzes user profile to determine risk tolerance and investment capacity
    """
    profile_str = str(context.user_profile)
    result = await risk_agent.assess_risk(profile_str)
    context.risk_assessment = {"raw": result}
    context.history.append(copy.deepcopy(context.model_dump()))
    return context

async def market_analysis_node(context: FAPContext) -> FAPContext:
    """
    Step 2: Market Analysis Node
    Analyzes current market conditions and trends
    """
    result = await market_agent.analyze_market("current")
    context.market_analysis = {"raw": result}
    context.history.append(copy.deepcopy(context.model_dump()))
    return context

async def portfolio_generation_node(context: FAPContext) -> FAPContext:
    """
    Step 3: Portfolio Generation Node
    Creates personalized portfolio allocation based on risk assessment and market analysis
    """
    profile_str = str(context.user_profile)
    result = await portfolio_agent.generate_portfolio(profile_str)
    context.portfolio_allocation = {"raw": result}
    context.history.append(copy.deepcopy(context.model_dump()))
    return context

async def report_generation_node(context: FAPContext) -> FAPContext:
    """
    Step 4: Report Generation Node
    Compiles comprehensive investment report from all previous analysis steps
    """
    # Compose a simple report from previous steps
    summary = context.risk_assessment.get("raw", "") if context.risk_assessment else ""
    outlook = context.market_analysis.get("raw", "") if context.market_analysis else ""
    allocation = context.portfolio_allocation.get("raw", "") if context.portfolio_allocation else ""
    report = f"Financial Analysis Report\n{'='*50}\n\nRisk Assessment Summary:\n{summary}\n\nMarket Outlook:\n{outlook}\n\nRecommended Portfolio Allocation:\n{allocation}"
    context.report = report
    context.history.append(copy.deepcopy(context.model_dump()))
    return context 