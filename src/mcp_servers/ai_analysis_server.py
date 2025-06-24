"""
AI Analysis MCP Server
Provides standardized access to OpenAI API for financial analysis
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from mcp.server import Server
from mcp.types import (
    Tool, 
    TextContent, 
    CallToolResult,
    ListToolsResult
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIAnalysisMCPServer:
    """MCP Server for AI-powered financial analysis"""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        logger.info("AI Analysis MCP Server initialized")
        
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not set. AI Analysis features require OpenAI API key.")
        
        # Initialize OpenAI LLM
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.7,
            api_key=self.openai_api_key
        )
        
        # Initialize MCP server
        self.server = Server("ai-analysis-server")
        self._register_tools()
    
    def _register_tools(self):
        """Register all available AI analysis tools"""
        
        @self.server.list_tools()
        async def list_tools() -> ListToolsResult:
            """List all available AI analysis tools"""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="analyze_portfolio",
                        description="Generate comprehensive portfolio analysis and recommendations",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "user_profile": {
                                    "type": "object",
                                    "description": "User profile information including age, income, risk tolerance",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "age": {"type": "integer"},
                                        "income": {"type": "number"},
                                        "risk_tolerance": {"type": "string"},
                                        "investment_goal": {"type": "string"},
                                        "investment_horizon": {"type": "string"}
                                    },
                                    "required": ["age", "income", "risk_tolerance"]
                                },
                                "market_data": {
                                    "type": "object",
                                    "description": "Current market data and conditions"
                                },
                                "analysis_type": {
                                    "type": "string",
                                    "enum": ["comprehensive", "allocation", "risk_assessment", "rebalancing"],
                                    "description": "Type of analysis to perform",
                                    "default": "comprehensive"
                                }
                            },
                            "required": ["user_profile"]
                        }
                    ),
                    Tool(
                        name="assess_risk",
                        description="Perform detailed risk assessment based on user profile",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "user_profile": {
                                    "type": "object",
                                    "description": "User profile information"
                                },
                                "current_portfolio": {
                                    "type": "object",
                                    "description": "Current portfolio allocation",
                                    "default": {}
                                }
                            },
                            "required": ["user_profile"]
                        }
                    ),
                    Tool(
                        name="generate_market_insights",
                        description="Generate AI-powered market analysis and insights",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "market_data": {
                                    "type": "object",
                                    "description": "Market data to analyze"
                                },
                                "symbol": {
                                    "type": "string",
                                    "description": "Primary symbol to focus analysis on",
                                    "default": "SPY"
                                },
                                "period": {
                                    "type": "string",
                                    "description": "Time period for analysis",
                                    "default": "1d"
                                },
                                "analysis_focus": {
                                    "type": "string",
                                    "enum": ["technical", "fundamental", "sentiment", "comprehensive"],
                                    "description": "Focus area for analysis",
                                    "default": "comprehensive"
                                }
                            },
                            "required": ["market_data"]
                        }
                    ),
                    Tool(
                        name="generate_investment_proposal",
                        description="Generate specific investment proposals and actionable recommendations",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "user_profile": {
                                    "type": "object",
                                    "description": "User profile information"
                                },
                                "portfolio_allocation": {
                                    "type": "object",
                                    "description": "Recommended portfolio allocation"
                                },
                                "market_conditions": {
                                    "type": "object",
                                    "description": "Current market conditions"
                                },
                                "proposal_type": {
                                    "type": "string",
                                    "enum": ["initial", "rebalancing", "tactical"],
                                    "description": "Type of investment proposal",
                                    "default": "initial"
                                }
                            },
                            "required": ["user_profile", "portfolio_allocation"]
                        }
                    )
                ]
            )
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Handle tool calls"""
            try:
                if name == "analyze_portfolio":
                    result = await self._analyze_portfolio(**arguments)
                elif name == "assess_risk":
                    result = await self._assess_risk(**arguments)
                elif name == "generate_market_insights":
                    result = await self._generate_market_insights(**arguments)
                elif name == "generate_investment_proposal":
                    result = await self._generate_investment_proposal(**arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
                
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=json.dumps(result, default=str)
                    )]
                )
                
            except Exception as e:
                logger.error(f"Error in tool {name}: {str(e)}")
                return CallToolResult(
                    content=[TextContent(
                        type="text", 
                        text=json.dumps({"error": str(e)})
                    )],
                    isError=True
                )
    
    async def _analyze_portfolio(self, user_profile: Dict[str, Any], market_data: Dict[str, Any] = None, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """Generate comprehensive portfolio analysis"""
        try:
            # Create analysis prompt based on type
            if analysis_type == "allocation":
                prompt_template = ChatPromptTemplate.from_template("""
                You are a professional financial advisor. Based on the user profile provided, generate an optimal portfolio allocation.
                
                User Profile:
                - Age: {age}
                - Income: ${income:,.2f}
                - Risk Tolerance: {risk_tolerance}
                - Investment Goal: {investment_goal}
                - Investment Horizon: {investment_horizon}
                
                Please provide:
                1. Recommended asset allocation percentages for: Stocks, Bonds, Cash, Real Estate, Commodities, Cryptocurrency, ETFs, REITs
                2. Rationale for each allocation
                3. Expected annual return and risk level
                4. Rebalancing recommendations
                
                Format the allocation as a JSON object with asset classes as keys and percentages as values.
                Ensure all percentages sum to 100%.
                """)
            
            elif analysis_type == "risk_assessment":
                prompt_template = ChatPromptTemplate.from_template("""
                You are a risk assessment specialist. Analyze the user's risk profile and provide detailed risk analysis.
                
                User Profile:
                - Age: {age}
                - Income: ${income:,.2f}
                - Risk Tolerance: {risk_tolerance}
                - Investment Goal: {investment_goal}
                - Investment Horizon: {investment_horizon}
                
                Provide:
                1. Risk score (1-10 scale)
                2. Risk capacity analysis
                3. Risk tolerance vs capacity comparison
                4. Recommendations for risk management
                5. Stress testing scenarios
                """)
            
            else:  # comprehensive
                prompt_template = ChatPromptTemplate.from_template("""
                You are a comprehensive financial advisor. Provide a complete investment analysis and recommendation.
                
                User Profile:
                - Name: {name}
                - Age: {age}
                - Income: ${income:,.2f}
                - Risk Tolerance: {risk_tolerance}
                - Investment Goal: {investment_goal}
                - Investment Horizon: {investment_horizon}
                
                Market Data Summary: {market_data}
                
                Provide a comprehensive analysis including:
                1. Portfolio Allocation (specific percentages for 8 asset classes)
                2. Investment Strategy Summary
                3. Risk Analysis
                4. Market Outlook Impact  
                5. Specific Recommendations
                6. Timeline and Action Steps
                
                Ensure the allocation percentages sum to 100% and are appropriate for the risk tolerance:
                - Conservative: Lower stocks (20-30%), higher bonds (40-50%), stable assets
                - Moderate: Balanced stocks (45-55%), moderate bonds (25-35%), diversified
                - Aggressive: Higher stocks (60-70%), lower bonds (10-20%), growth-focused
                """)
            
            # Format input data
            input_data = {
                "name": user_profile.get("name", "Client"),
                "age": user_profile.get("age", 30),
                "income": user_profile.get("income", 50000),
                "risk_tolerance": user_profile.get("risk_tolerance", "Moderate"),
                "investment_goal": user_profile.get("investment_goal", "Wealth Building"),
                "investment_horizon": user_profile.get("investment_horizon", "Long-term"),
                "market_data": json.dumps(market_data) if market_data else "No current market data provided"
            }
            
            # Generate analysis
            chain = prompt_template | self.llm | StrOutputParser()
            analysis_result = await chain.ainvoke(input_data)
            
            return {
                "analysis_type": analysis_type,
                "user_profile": user_profile,
                "analysis_result": analysis_result,
                "timestamp": datetime.now().isoformat(),
                "model_used": "gpt-4-turbo-preview"
            }
            
        except Exception as e:
            logger.error(f"Error in portfolio analysis: {str(e)}")
            raise ValueError(f"Failed to analyze portfolio: {str(e)}")
    
    async def _assess_risk(self, user_profile: Dict[str, Any], current_portfolio: Dict[str, Any] = None) -> Dict[str, Any]:
        """Perform detailed risk assessment"""
        try:
            prompt_template = ChatPromptTemplate.from_template("""
            You are a risk assessment specialist. Provide a detailed risk analysis.
            
            User Profile:
            - Age: {age}
            - Income: ${income:,.2f}
            - Risk Tolerance: {risk_tolerance}
            - Investment Goal: {investment_goal}
            - Investment Horizon: {investment_horizon}
            
            Current Portfolio: {current_portfolio}
            
            Provide a JSON response with:
            {{
                "risk_score": <number 1-10>,
                "risk_capacity": "<High/Medium/Low>",
                "risk_tolerance_assessment": "<Conservative/Moderate/Aggressive>",
                "capacity_vs_tolerance": "<Aligned/Capacity Higher/Tolerance Higher>",
                "recommendations": ["<recommendation1>", "<recommendation2>"],
                "stress_scenarios": [
                    {{
                        "scenario": "<scenario_name>",
                        "potential_loss": "<percentage>",
                        "recovery_time": "<time_estimate>"
                    }}
                ]
            }}
            """)
            
            input_data = {
                "age": user_profile.get("age", 30),
                "income": user_profile.get("income", 50000),
                "risk_tolerance": user_profile.get("risk_tolerance", "Moderate"),
                "investment_goal": user_profile.get("investment_goal", "Wealth Building"),
                "investment_horizon": user_profile.get("investment_horizon", "Long-term"),
                "current_portfolio": json.dumps(current_portfolio) if current_portfolio else "No current portfolio"
            }
            
            chain = prompt_template | self.llm | StrOutputParser()
            risk_analysis = await chain.ainvoke(input_data)
            
            return {
                "user_profile": user_profile,
                "risk_analysis": risk_analysis,
                "timestamp": datetime.now().isoformat(),
                "model_used": "gpt-4-turbo-preview"
            }
            
        except Exception as e:
            logger.error(f"Error in risk assessment: {str(e)}")
            raise ValueError(f"Failed to assess risk: {str(e)}")
    
    async def _generate_market_insights(self, market_data: Dict[str, Any], symbol: str = "SPY", period: str = "1d", analysis_focus: str = "comprehensive") -> Dict[str, Any]:
        """Generate AI-powered market insights"""
        try:
            prompt_template = ChatPromptTemplate.from_template("""
            You are a market analysis expert. Analyze the provided market data and generate insights.
            
            Primary Symbol: {symbol}
            Analysis Period: {period}
            Analysis Focus: {analysis_focus}
            
            Market Data:
            {market_data}
            
            Provide analysis covering:
            1. Current market conditions summary
            2. Key trends and patterns identified
            3. Price action analysis
            4. Volume and momentum indicators
            5. Risk factors and opportunities
            6. Short-term and medium-term outlook
            7. Investment implications
            
            Format as a comprehensive market insights report.
            """)
            
            input_data = {
                "symbol": symbol,
                "period": period,
                "analysis_focus": analysis_focus,
                "market_data": json.dumps(market_data, indent=2, default=str)
            }
            
            chain = prompt_template | self.llm | StrOutputParser()
            market_insights = await chain.ainvoke(input_data)
            
            return {
                "symbol": symbol,
                "period": period,
                "analysis_focus": analysis_focus,
                "market_insights": market_insights,
                "market_data_summary": self._summarize_market_data(market_data),
                "timestamp": datetime.now().isoformat(),
                "model_used": "gpt-4-turbo-preview"
            }
            
        except Exception as e:
            logger.error(f"Error generating market insights: {str(e)}")
            raise ValueError(f"Failed to generate market insights: {str(e)}")
    
    async def _generate_investment_proposal(self, user_profile: Dict[str, Any], portfolio_allocation: Dict[str, Any], market_conditions: Dict[str, Any] = None, proposal_type: str = "initial") -> Dict[str, Any]:
        """Generate specific investment proposals"""
        try:
            prompt_template = ChatPromptTemplate.from_template("""
            You are an investment advisor creating actionable investment proposals.
            
            User Profile:
            - Name: {name}
            - Age: {age}
            - Income: ${income:,.2f}
            - Risk Tolerance: {risk_tolerance}
            - Investment Goal: {investment_goal}
            - Investment Horizon: {investment_horizon}
            
            Recommended Portfolio Allocation:
            {portfolio_allocation}
            
            Market Conditions: {market_conditions}
            Proposal Type: {proposal_type}
            
            Create a detailed investment proposal including:
            1. Executive Summary
            2. Specific investment recommendations (ETFs, mutual funds, individual stocks)
            3. Dollar amounts for each investment (based on income/capacity)
            4. Implementation timeline
            5. Monitoring and rebalancing schedule
            6. Exit strategies and risk management
            7. Expected returns and timeline
            
            Make recommendations specific and actionable with actual fund/stock symbols where appropriate.
            """)
            
            input_data = {
                "name": user_profile.get("name", "Client"),
                "age": user_profile.get("age", 30),
                "income": user_profile.get("income", 50000),
                "risk_tolerance": user_profile.get("risk_tolerance", "Moderate"),
                "investment_goal": user_profile.get("investment_goal", "Wealth Building"),
                "investment_horizon": user_profile.get("investment_horizon", "Long-term"),
                "portfolio_allocation": json.dumps(portfolio_allocation, indent=2),
                "market_conditions": json.dumps(market_conditions) if market_conditions else "Standard market conditions assumed",
                "proposal_type": proposal_type
            }
            
            chain = prompt_template | self.llm | StrOutputParser()
            investment_proposal = await chain.ainvoke(input_data)
            
            return {
                "proposal_type": proposal_type,
                "user_profile": user_profile,
                "portfolio_allocation": portfolio_allocation,
                "investment_proposal": investment_proposal,
                "timestamp": datetime.now().isoformat(),
                "model_used": "gpt-4-turbo-preview"
            }
            
        except Exception as e:
            logger.error(f"Error generating investment proposal: {str(e)}")
            raise ValueError(f"Failed to generate investment proposal: {str(e)}")
    
    def _summarize_market_data(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary of market data for analysis"""
        summary = {
            "data_points": len(market_data),
            "timestamp": datetime.now().isoformat()
        }
        
        # Extract key metrics if available
        if isinstance(market_data, dict):
            if "symbols" in market_data:
                summary["symbols_analyzed"] = list(market_data["symbols"].keys())
            if "market_sentiment" in market_data:
                summary["market_sentiment"] = market_data["market_sentiment"]
        
        return summary

# Server instance
ai_analysis_server = AIAnalysisMCPServer()

async def main():
    """Run the MCP server"""
    # Import here to avoid circular imports
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await ai_analysis_server.server.run(
            read_stream, 
            write_stream,
            ai_analysis_server.server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main()) 