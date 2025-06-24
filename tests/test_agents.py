"""
Tests for the financial advisor agents
"""

import pytest
from unittest.mock import AsyncMock, patch
from src.agents.market_analysis_agent import MarketAnalysisAgent, MarketAnalysisOutput
from src.agents.risk_assessment_agent import RiskAssessmentAgent, RiskProfile, RiskAssessment
from src.agents.portfolio_agent import PortfolioAgent, PortfolioAllocation, PortfolioAnalysis
from tests.mocks import MOCK_MARKET_DATA, MOCK_PORTFOLIO, MOCK_RISK_PROFILE

@pytest.fixture
def mock_market_data_service():
    """Mock market data service"""
    with patch('src.services.market_data_service.MarketDataService') as mock:
        mock_instance = mock.return_value
        mock_instance.get_market_summary = AsyncMock(return_value=MOCK_MARKET_DATA)
        yield mock_instance

@pytest.mark.asyncio
async def test_market_analysis_agent(mock_market_data_service):
    """Test the market analysis agent"""
    agent = MarketAnalysisAgent(market_data_service=mock_market_data_service)
    
    # Test market analysis
    analysis = await agent.analyze_market("What's the current market condition?")
    assert isinstance(analysis, MarketAnalysisOutput)
    assert analysis.current_price == 450.25
    assert analysis.market_sentiment == "Bullish"
    assert analysis.timestamp == "2024-03-20T10:00:00Z"

@pytest.mark.asyncio
async def test_risk_assessment_agent():
    """Test the risk assessment agent"""
    agent = RiskAssessmentAgent()
    
    # Test risk assessment
    profile = "I am a 35 year old with $150,000 annual income and moderate risk tolerance"
    assessment = await agent.assess_risk(profile)
    assert isinstance(assessment, RiskAssessment)
    assert 0 <= assessment.risk_score <= 1
    assert assessment.risk_level in ["Low", "Moderate", "High"]
    assert isinstance(assessment.recommendations, list)
    
    # Verify profile data
    assert assessment.profile_analysis["age"] == "35 years"
    assert assessment.profile_analysis["income"] == "$150,000"

@pytest.mark.asyncio
async def test_portfolio_agent():
    """Test the portfolio agent"""
    agent = PortfolioAgent()
    
    # Test portfolio generation
    allocation = await agent.generate_portfolio("moderate")
    assert isinstance(allocation, PortfolioAllocation)
    assert abs(sum(allocation.model_dump().values()) - 1.0) < 0.0001
    assert allocation.stocks == 0.5
    assert allocation.bonds == 0.25
    assert allocation.cash == 0.1
    assert allocation.real_estate == 0.05
    assert allocation.commodities == 0.05
    assert allocation.cryptocurrency == 0.02
    assert allocation.etfs == 0.02
    assert allocation.reits == 0.01
    
    # Test portfolio analysis
    analysis = await agent.analyze_portfolio_performance(MOCK_PORTFOLIO)
    assert isinstance(analysis, PortfolioAnalysis)
    assert 0 <= analysis.diversification_score <= 100
    assert isinstance(analysis.rebalancing_needed, bool)
    
    # Test portfolio rebalancing
    target_allocation = {
        "stocks": 0.6,
        "bonds": 0.3,
        "cash": 0.05,
        "real_estate": 0.05
    }
    rebalancing = await agent.rebalance_portfolio(MOCK_PORTFOLIO, target_allocation)
    assert isinstance(rebalancing, dict)

@pytest.mark.asyncio
async def test_agent_workflow(mock_market_data_service):
    """Test the complete agent workflow"""
    market_agent = MarketAnalysisAgent(market_data_service=mock_market_data_service)
    risk_agent = RiskAssessmentAgent()
    portfolio_agent = PortfolioAgent()
    
    # Test market analysis
    market_analysis = await market_agent.analyze_market("What's the current market condition?")
    assert isinstance(market_analysis, MarketAnalysisOutput)
    assert market_analysis.current_price == 450.25
    
    # Test risk assessment
    risk_assessment = await risk_agent.assess_risk("I am a 35 year old with $150,000 annual income and moderate risk tolerance")
    assert isinstance(risk_assessment, RiskAssessment)
    assert risk_assessment.risk_level == "Moderate"
    
    # Test portfolio generation based on risk assessment
    portfolio = await portfolio_agent.generate_portfolio(risk_assessment.risk_level.lower())
    assert isinstance(portfolio, PortfolioAllocation)
    assert portfolio.stocks == 0.6  # Moderate risk allocation 