"""
Market Analysis Agent for analyzing market conditions and trends
"""

import os
from typing import Dict, List, Optional
import logging
from langchain_core.tools import Tool
from pydantic import BaseModel, Field
from .base_agent import BaseFinancialAgent
from src.services.market_data_service import MarketDataService

logger = logging.getLogger(__name__)

class MarketAnalysisOutput(BaseModel):
    """Structured output for market analysis"""
    current_price: float = Field(description="Current price of the analyzed security")
    daily_change: float = Field(description="Daily price change")
    daily_change_percent: float = Field(description="Daily price change percentage")
    volume: int = Field(description="Trading volume")
    market_sentiment: str = Field(description="Overall market sentiment")
    timestamp: str = Field(description="Timestamp of the analysis")

class MarketAnalysisAgent(BaseFinancialAgent):
    """Agent responsible for market analysis and insights"""
    
    def __init__(self, market_data_service=None):
        self.market_data_service = market_data_service or MarketDataService()
        # Define tools
        tools = [
            Tool(
                name="get_market_summary",
                func=self.market_data_service.get_market_summary,
                description="Get a summary of current market conditions"
            ),
            Tool(
                name="get_stock_data",
                func=self.market_data_service.get_stock_data,
                description="Get the current price of a specific stock"
            )
        ]
        
        # Initialize with custom system prompt
        system_prompt = """You are a market analysis expert. Your role is to:
        1. Analyze market conditions and trends
        2. Provide insights on market movements
        3. Explain market sentiment
        4. Offer data-driven market analysis
        
        Always provide clear, concise, and accurate market analysis."""
        
        super().__init__(
            tools=tools,
            system_prompt=system_prompt
        )
    
    async def analyze_market(self, query: str) -> MarketAnalysisOutput:
        """Analyze market conditions and provide structured insights"""
        try:
            # Get market summary
            market_summary = await self.market_data_service.get_market_summary()
            
            if "error" in market_summary:
                raise ValueError(f"Error analyzing market conditions: {market_summary['error']}")
            
            # Extract data from sources
            alpha_data = market_summary["sources"]["alpha_vantage"]
            spy_data = alpha_data.get("SPY", {})
            
            # Create structured output
            return MarketAnalysisOutput(
                current_price=float(spy_data.get("price", 0)),
                daily_change=float(spy_data.get("change", 0)),
                daily_change_percent=float(spy_data.get("change_percent", 0)),
                volume=int(spy_data.get("volume", 0)),
                market_sentiment=market_summary["market_sentiment"],
                timestamp=market_summary["timestamp"]
            )
            
        except Exception as e:
            logger.error(f"Error in market analysis: {str(e)}")
            raise
    
    async def process_message(self, message: str, chat_history: List[Dict[str, str]] = None) -> str:
        """Process a message and return a response"""
        try:
            # Get structured analysis
            analysis = await self.analyze_market(message)
            
            # Format the response
            response = [
                f"Current S&P 500 (SPY) Price: ${analysis.current_price:.2f}",
                f"Daily Change: ${analysis.daily_change:.2f} ({analysis.daily_change_percent:.2f}%)",
                f"Trading Volume: {analysis.volume:,}",
                f"\nMarket Sentiment: {analysis.market_sentiment}",
                f"\nData as of: {analysis.timestamp}"
            ]
            
            return "\n".join(response)
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return f"I apologize, but I encountered an error: {str(e)}" 