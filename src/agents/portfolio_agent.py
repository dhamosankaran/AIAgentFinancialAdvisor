"""
Portfolio Management Agent for generating investment recommendations
"""

from typing import Dict, List, Optional
from langchain_core.tools import Tool
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
import numpy as np
from datetime import datetime, timedelta

from .base_agent import BaseFinancialAgent

class PortfolioAllocation(BaseModel):
    """Structured output for portfolio allocation"""
    stocks: float = Field(description="Percentage allocation to stocks")
    bonds: float = Field(description="Percentage allocation to bonds")
    cash: float = Field(description="Percentage allocation to cash")
    real_estate: float = Field(description="Percentage allocation to real estate")
    commodities: float = Field(description="Percentage allocation to commodities")
    cryptocurrency: float = Field(description="Percentage allocation to cryptocurrency")
    etfs: float = Field(description="Percentage allocation to ETFs")
    reits: float = Field(description="Percentage allocation to REITs")

class PortfolioAnalysis(BaseModel):
    """Structured output for portfolio analysis"""
    current_allocation: Dict[str, float] = Field(description="Current portfolio allocation")
    diversification_score: float = Field(description="Portfolio diversification score (0-100)")
    rebalancing_needed: bool = Field(description="Whether portfolio rebalancing is needed")
    rebalancing_suggestions: Dict[str, float] = Field(description="Suggested rebalancing changes")

class PortfolioAgent(BaseFinancialAgent):
    """Agent responsible for portfolio management and recommendations"""
    
    def __init__(
        self,
        llm: Optional[ChatOpenAI] = None,
        tools: Optional[List[Tool]] = None,
    ):
        # Define system prompt for portfolio management
        system_prompt = """You are an expert portfolio management agent. Your role is to:
        1. Generate personalized investment portfolios
        2. Analyze portfolio performance
        3. Suggest portfolio rebalancing
        4. Provide portfolio optimization recommendations
        
        Always consider the user's risk profile, investment goals, and market conditions when making portfolio decisions."""
        
        # Define portfolio management tools
        portfolio_tools = [
            Tool(
                name="generate_portfolio",
                func=self.generate_portfolio,
                description="Generate a portfolio based on user profile and risk assessment"
            ),
            Tool(
                name="analyze_portfolio_performance",
                func=self.analyze_portfolio_performance,
                description="Analyze the performance of a given portfolio"
            ),
            Tool(
                name="rebalance_portfolio",
                func=self.rebalance_portfolio,
                description="Suggest portfolio rebalancing based on current allocation and target allocation"
            ),
        ]
        
        # Combine provided tools with portfolio tools
        all_tools = (tools or []) + portfolio_tools
        
        # Initialize base class
        super().__init__(
            llm=llm,
            tools=all_tools,
            system_prompt=system_prompt
        )
    
    async def generate_portfolio(self, profile: Dict | str) -> PortfolioAllocation:
        """Generate a portfolio based on user profile and risk assessment."""
        try:
            # Handle both string and dictionary inputs
            if isinstance(profile, str):
                risk_level = profile.lower()
            else:
                risk_level = profile.get("risk_level", "moderate").lower()
            
            # Define target allocations based on risk level
            allocations = {
                "conservative": {
                    "stocks": 0.25,
                    "bonds": 0.45,
                    "cash": 0.15,
                    "real_estate": 0.05,
                    "commodities": 0.05,
                    "cryptocurrency": 0.00,
                    "etfs": 0.03,
                    "reits": 0.02
                },
                "moderate": {
                    "stocks": 0.50,
                    "bonds": 0.25,
                    "cash": 0.10,
                    "real_estate": 0.05,
                    "commodities": 0.05,
                    "cryptocurrency": 0.02,
                    "etfs": 0.02,
                    "reits": 0.01
                },
                "aggressive": {
                    "stocks": 0.65,
                    "bonds": 0.15,
                    "cash": 0.05,
                    "real_estate": 0.05,
                    "commodities": 0.05,
                    "cryptocurrency": 0.03,
                    "etfs": 0.01,
                    "reits": 0.01
                }
            }
            
            # Get allocation for risk level
            target_allocation = allocations.get(risk_level, allocations["moderate"])
            
            return PortfolioAllocation(**target_allocation)
            
        except Exception as e:
            self.logger.error(f"Error generating portfolio: {str(e)}")
            raise
    
    async def analyze_portfolio_performance(self, portfolio: Dict[str, float]) -> PortfolioAnalysis:
        """Analyze the performance of a given portfolio."""
        try:
            # Calculate portfolio metrics
            total_value = sum(portfolio.values())
            if total_value == 0:
                raise ValueError("Portfolio is empty")
            
            # Calculate allocation percentages
            current_allocation = {
                asset: (value / total_value) * 100
                for asset, value in portfolio.items()
            }
            
            # Calculate diversification score
            diversification_score = await self._calculate_diversification_score(current_allocation)
            
            # Check if rebalancing is needed
            rebalancing_needed = any(abs(alloc - 25) > 5 for alloc in current_allocation.values())
            
            # Generate rebalancing suggestions
            rebalancing_suggestions = {}
            if rebalancing_needed:
                for asset, current in current_allocation.items():
                    target = 25  # Equal allocation target
                    diff = target - current
                    if abs(diff) > 5:  # Only suggest changes if difference is more than 5%
                        rebalancing_suggestions[asset] = diff
            
            return PortfolioAnalysis(
                current_allocation=current_allocation,
                diversification_score=diversification_score,
                rebalancing_needed=rebalancing_needed,
                rebalancing_suggestions=rebalancing_suggestions
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing portfolio performance: {str(e)}")
            raise
    
    async def rebalance_portfolio(self, current_portfolio: Dict[str, float], target_allocation: Dict[str, float]) -> Dict[str, float]:
        """Suggest portfolio rebalancing based on current and target allocations."""
        try:
            total_value = sum(current_portfolio.values())
            if total_value == 0:
                raise ValueError("Portfolio is empty")
            
            # Calculate current allocation percentages
            current_allocation = {
                asset: (value / total_value) * 100
                for asset, value in current_portfolio.items()
            }
            
            # Calculate rebalancing needs
            rebalancing = {}
            for asset in set(current_allocation.keys()) | set(target_allocation.keys()):
                current = current_allocation.get(asset, 0)
                target = target_allocation.get(asset, 0)
                diff = target - current
                if abs(diff) > 1:  # Only suggest changes if difference is more than 1%
                    rebalancing[asset] = diff
            
            return rebalancing
            
        except Exception as e:
            self.logger.error(f"Error suggesting rebalancing: {str(e)}")
            raise
    
    async def _calculate_diversification_score(self, allocation: Dict[str, float]) -> float:
        """Calculate a diversification score based on portfolio allocation."""
        try:
            # Calculate Herfindahl-Hirschman Index (HHI)
            hhi = sum((percentage / 100) ** 2 for percentage in allocation.values())
            
            # Convert HHI to a 0-100 score (lower HHI = higher diversification)
            diversification_score = (1 - hhi) * 100
            
            return diversification_score
        except Exception as e:
            self.logger.error(f"Error calculating diversification score: {str(e)}")
            return 0.0
    
    async def process_message(self, message: str, chat_history: List[Dict[str, str]] = None) -> str:
        """Process a message and return a response"""
        try:
            # Generate portfolio allocation
            allocation = await self.generate_portfolio(message)
            
            # Format the response
            response = [
                f"Recommended Portfolio Allocation:",
                *[f"{asset.capitalize()}: {weight*100:.1f}%" for asset, weight in allocation.model_dump().items()]
            ]
            
            return "\n".join(response)
            
        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}")
            return f"I apologize, but I encountered an error: {str(e)}" 