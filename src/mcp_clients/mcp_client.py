"""
Unified MCP Client for AgenticAI
Provides standardized access to MCP servers with REAL API calls
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import os
import aiohttp
import yfinance as yf
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import LangSmith service for tracing
try:
    from src.services.langsmith_service import langsmith_service
    LANGSMITH_AVAILABLE = True
    logger.info("✅ LangSmith tracing enabled for MCP Client")
except ImportError:
    LANGSMITH_AVAILABLE = False
    logger.warning("⚠️ LangSmith not available - tracing disabled")

class MCPClient:
    """Unified MCP Client for AgenticAI application with REAL API calls"""
    
    def __init__(self):
        self.connected = False
        self.available_tools = {}
        
        # Load API keys from environment
        self.alpha_vantage_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Initialize OpenAI client if key is available
        if self.openai_api_key:
            self.llm = ChatOpenAI(
                model="gpt-4-turbo-preview",
                temperature=0.7,
                api_key=self.openai_api_key
            )
            logger.info("✅ OpenAI LLM initialized for REAL API calls")
        else:
            logger.warning("⚠️ OPENAI_API_KEY not found - AI analysis features limited")
            
        if self.alpha_vantage_key:
            logger.info("✅ Alpha Vantage API key found - REAL market data enabled")
        else:
            logger.warning("⚠️ ALPHA_VANTAGE_API_KEY not found - using Yahoo Finance fallback")
        
        logger.info("🚀 MCP Client initialized with REAL API integration")
    
    async def initialize(self):
        """Initialize MCP clients and discover tools"""
        try:
            # Discover available tools
            await self._discover_tools()
            
            self.connected = True
            logger.info("✅ MCP Client successfully initialized with REAL API connections")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize MCP Client: {str(e)}")
            raise
    
    async def _discover_tools(self):
        """Discover available tools for real API calls"""
        self.available_tools = {
            "market_data": {
                "get_stock_quote": {
                    "description": "Get real-time stock quote using Alpha Vantage or Yahoo Finance API",
                    "uses_real_api": True
                },
                "get_historical_data": {
                    "description": "Get historical market data using Yahoo Finance API",
                    "uses_real_api": True
                },
                "get_market_indices": {
                    "description": "Get major market indices using real API calls",
                    "uses_real_api": True
                },
                "get_market_summary": {
                    "description": "Get comprehensive market summary with real data",
                    "uses_real_api": True
                }
            }
        }
        
        # Add AI analysis tools if OpenAI key is available
        if self.openai_api_key:
            self.available_tools["ai_analysis"] = {
                "analyze_portfolio": {
                    "description": "Generate comprehensive portfolio analysis using OpenAI GPT-4",
                    "uses_real_api": True
                },
                "assess_risk": {
                    "description": "Perform detailed risk assessment using OpenAI API",
                    "uses_real_api": True
                },
                "generate_market_insights": {
                    "description": "Generate AI-powered market insights using OpenAI GPT-4",
                    "uses_real_api": True
                },
                "generate_investment_proposal": {
                    "description": "Generate investment proposals using OpenAI API",
                    "uses_real_api": True
                }
            }
        
        logger.info(f"📊 Discovered {len(self.available_tools)} tool categories with REAL API integration")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any] = None, server_type: str = None) -> Dict[str, Any]:
        """Call a tool using REAL API calls with LangSmith tracing"""
        if not self.connected:
            raise RuntimeError("MCP Client not connected. Call initialize() first.")
        
        logger.info(f"🔄 Making REAL API call: {tool_name}")
        
        # Apply LangSmith tracing if available
        if LANGSMITH_AVAILABLE:
            @langsmith_service.trace_mcp_request(server_type or "unknown", tool_name)
            async def traced_call():
                return await self._execute_tool_call(tool_name, arguments, server_type)
            
            return await traced_call()
        else:
            return await self._execute_tool_call(tool_name, arguments, server_type)
    
    async def _execute_tool_call(self, tool_name: str, arguments: Dict[str, Any], server_type: str) -> Dict[str, Any]:
        """Execute the actual tool call"""
        try:
            if server_type == "market_data" or tool_name in ["get_stock_quote", "get_historical_data", "get_market_indices", "get_market_summary"]:
                return await self._real_market_data_call(tool_name, arguments or {})
            
            elif server_type == "ai_analysis" or tool_name in ["analyze_portfolio", "assess_risk", "generate_market_insights", "generate_investment_proposal"]:
                return await self._real_ai_analysis_call(tool_name, arguments or {})
            
            else:
                raise ValueError(f"Unknown tool: {tool_name}")
                
        except Exception as e:
            logger.error(f"❌ Error calling tool {tool_name}: {str(e)}")
            raise
    
    async def _real_market_data_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Make REAL market data API calls"""
        logger.info(f"📈 REAL MARKET DATA API CALL: {tool_name}")
        
        if tool_name == "get_stock_quote":
            symbol = arguments.get("symbol", "SPY")
            source = arguments.get("source", "alpha_vantage")
            
            if source == "alpha_vantage" and self.alpha_vantage_key:
                return await self._get_alpha_vantage_quote(symbol)
            else:
                return await self._get_yahoo_quote(symbol)
        
        elif tool_name == "get_historical_data":
            symbol = arguments.get("symbol", "SPY")
            period = arguments.get("period", "1d")
            interval = arguments.get("interval", "1h")
            return await self._get_yahoo_historical(symbol, period, interval)
        
        elif tool_name == "get_market_indices":
            return await self._get_market_indices()
        
        elif tool_name == "get_market_summary":
            symbols = arguments.get("symbols", ["SPY"])
            return await self._get_market_summary(symbols)
        
        else:
            raise ValueError(f"Unknown market data tool: {tool_name}")
    
    async def _get_alpha_vantage_quote(self, symbol: str) -> Dict[str, Any]:
        """Get real stock quote from Alpha Vantage API"""
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": self.alpha_vantage_key
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if "Global Quote" in data:
                            quote = data["Global Quote"]
                            result = {
                                "symbol": symbol,
                                "source": "alpha_vantage_real_api",
                                "price": float(quote.get("05. price", 0)),
                                "change": float(quote.get("09. change", 0)),
                                "change_percent": float(quote.get("10. change percent", "0%").strip("%")),
                                "volume": int(quote.get("06. volume", 0)),
                                "high": float(quote.get("03. high", 0)),
                                "low": float(quote.get("04. low", 0)),
                                "open": float(quote.get("02. open", 0)),
                                "previous_close": float(quote.get("08. previous close", 0)),
                                "timestamp": datetime.now().isoformat(),
                                "api_call_successful": True
                            }
                            logger.info(f"✅ SUCCESS: Alpha Vantage API call for {symbol} - Price: ${result['price']}")
                            return result
                        else:
                            logger.warning(f"⚠️ Alpha Vantage API returned unexpected format, using Yahoo fallback")
                            return await self._get_yahoo_quote(symbol)
                    else:
                        logger.warning(f"⚠️ Alpha Vantage API returned status {response.status}, using Yahoo fallback")
                        return await self._get_yahoo_quote(symbol)
        except Exception as e:
            logger.error(f"❌ Error calling Alpha Vantage API: {str(e)}, using Yahoo fallback")
            return await self._get_yahoo_quote(symbol)
    
    async def _get_yahoo_quote(self, symbol: str) -> Dict[str, Any]:
        """Get real stock quote from Yahoo Finance API"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period="2d")
            
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                previous_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
                change = current_price - previous_close
                change_percent = (change / previous_close) * 100 if previous_close != 0 else 0
                
                result = {
                    "symbol": symbol,
                    "source": "yahoo_finance_real_api",
                    "price": float(current_price),
                    "change": float(change),
                    "change_percent": float(change_percent),
                    "volume": int(hist['Volume'].iloc[-1]) if 'Volume' in hist.columns else 0,
                    "high": float(hist['High'].iloc[-1]),
                    "low": float(hist['Low'].iloc[-1]),
                    "open": float(hist['Open'].iloc[-1]),
                    "previous_close": float(previous_close),
                    "timestamp": datetime.now().isoformat(),
                    "api_call_successful": True
                }
                logger.info(f"✅ SUCCESS: Yahoo Finance API call for {symbol} - Price: ${result['price']}")
                return result
            else:
                raise ValueError(f"No data available for symbol {symbol}")
                
        except Exception as e:
            logger.error(f"❌ Error calling Yahoo Finance API: {str(e)}")
            raise
    
    async def _get_yahoo_historical(self, symbol: str, period: str, interval: str) -> Dict[str, Any]:
        """Get real historical data from Yahoo Finance API"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period, interval=interval)
            
            if not hist.empty:
                result = {
                    "symbol": symbol,
                    "source": "yahoo_finance_real_api",
                    "data": hist.to_dict('records'),
                    "period": period,
                    "interval": interval,
                    "timestamp": datetime.now().isoformat(),
                    "api_call_successful": True,
                    "data_points": len(hist)
                }
                logger.info(f"✅ SUCCESS: Yahoo Finance historical data for {symbol} - {len(hist)} data points")
                return result
            else:
                raise ValueError(f"No historical data available for {symbol}")
                
        except Exception as e:
            logger.error(f"❌ Error getting historical data: {str(e)}")
            raise
    
    async def _get_market_indices(self) -> Dict[str, Any]:
        """Get real market indices data"""
        indices = ['^GSPC', '^IXIC', '^DJI', '^VIX']
        results = {}
        
        try:
            for index in indices:
                results[index] = await self._get_yahoo_quote(index)
            
            result = {
                "indices": results,
                "source": "real_api_calls",
                "timestamp": datetime.now().isoformat(),
                "api_call_successful": True
            }
            logger.info(f"✅ SUCCESS: Retrieved {len(results)} market indices via real API calls")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error getting market indices: {str(e)}")
            raise
    
    async def _get_market_summary(self, symbols: List[str]) -> Dict[str, Any]:
        """Get real market summary with multiple symbols"""
        summary = {}
        
        try:
            for symbol in symbols:
                summary[symbol] = await self._get_yahoo_quote(symbol)
            
            result = {
                "symbols": summary,
                "market_sentiment": "Data-driven analysis based on real market data",
                "source": "real_api_calls",
                "timestamp": datetime.now().isoformat(),
                "api_call_successful": True,
                "symbols_analyzed": len(summary)
            }
            logger.info(f"✅ SUCCESS: Market summary for {len(symbols)} symbols via real API calls")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error getting market summary: {str(e)}")
            raise
    
    async def _real_ai_analysis_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Make REAL AI analysis API calls using OpenAI"""
        if not self.openai_api_key:
            raise ValueError("OpenAI API key required for AI analysis tools")
        
        logger.info(f"🤖 REAL OPENAI API CALL: {tool_name}")
        
        try:
            if tool_name == "analyze_portfolio":
                return await self._real_analyze_portfolio(**arguments)
            elif tool_name == "assess_risk":
                return await self._real_assess_risk(**arguments)
            elif tool_name == "generate_market_insights":
                return await self._real_generate_market_insights(**arguments)
            elif tool_name == "generate_investment_proposal":
                return await self._real_generate_investment_proposal(**arguments)
            else:
                raise ValueError(f"Unknown AI analysis tool: {tool_name}")
                
        except Exception as e:
            logger.error(f"❌ Error in OpenAI API call for {tool_name}: {str(e)}")
            raise
    
    async def _real_analyze_portfolio(self, user_profile: Dict[str, Any], market_data: Dict[str, Any] = None, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """Real portfolio analysis using OpenAI API with LangSmith tracing"""
        prompt = ChatPromptTemplate.from_template(
            """As a professional financial advisor, analyze this portfolio and user profile:

User Profile:
- Age: {age}
- Income: ${income:,}
- Risk Tolerance: {risk_tolerance}
- Investment Goal: {investment_goal}
- Investment Horizon: {investment_horizon}

Market Data: {market_data}

Analysis Type: {analysis_type}

Provide a comprehensive analysis including:
1. Portfolio assessment based on user profile
2. Risk analysis specific to their situation
3. Asset allocation recommendations
4. Specific actionable recommendations
5. Market timing considerations

Keep recommendations practical and specific to their profile."""
        )
        
        try:
            # Apply LangSmith LLM tracing if available
            if LANGSMITH_AVAILABLE:
                @langsmith_service.trace_llm_call("portfolio_analysis")
                async def traced_llm_call():
                    chain = prompt | self.llm
                    return await chain.ainvoke({
                        "age": user_profile.get("age", "N/A"),
                        "income": user_profile.get("income", 0),
                        "risk_tolerance": user_profile.get("risk_tolerance", "moderate"),
                        "investment_goal": user_profile.get("investment_goal", "long-term growth"),
                        "investment_horizon": user_profile.get("investment_horizon", "long-term"),
                        "market_data": json.dumps(market_data) if market_data else "Current market conditions",
                        "analysis_type": analysis_type
                    })
                
                response = await traced_llm_call()
            else:
                chain = prompt | self.llm
                response = await chain.ainvoke({
                    "age": user_profile.get("age", "N/A"),
                    "income": user_profile.get("income", 0),
                    "risk_tolerance": user_profile.get("risk_tolerance", "moderate"),
                    "investment_goal": user_profile.get("investment_goal", "long-term growth"),
                    "investment_horizon": user_profile.get("investment_horizon", "long-term"),
                    "market_data": json.dumps(market_data) if market_data else "Current market conditions",
                    "analysis_type": analysis_type
                })
            
            result = {
                "analysis": response.content,
                "user_profile": user_profile,
                "analysis_type": analysis_type,
                "source": "openai_gpt4_real_api",
                "timestamp": datetime.now().isoformat(),
                "api_call_successful": True
            }
            
            logger.info("✅ SUCCESS: OpenAI portfolio analysis completed")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in OpenAI portfolio analysis: {str(e)}")
            raise
    
    async def _real_assess_risk(self, user_profile: Dict[str, Any], current_portfolio: Dict[str, Any] = None) -> Dict[str, Any]:
        """Real risk assessment using OpenAI API"""
        prompt = ChatPromptTemplate.from_template(
            """As a risk assessment specialist, evaluate the risk profile for this user:

User Profile:
- Age: {age}
- Income: ${income:,}
- Risk Tolerance: {risk_tolerance}
- Investment Goal: {investment_goal}
- Investment Horizon: {investment_horizon}

Current Portfolio: {current_portfolio}

Provide a detailed risk assessment including:
1. Overall risk score (1-10)
2. Risk factors specific to their situation
3. Recommended risk mitigation strategies
4. Portfolio adjustments to manage risk
5. Stress testing scenarios

Be specific and actionable in your recommendations."""
        )
        
        try:
            # Apply LangSmith LLM tracing if available
            if LANGSMITH_AVAILABLE:
                @langsmith_service.trace_llm_call("risk_assessment")
                async def traced_llm_call():
                    chain = prompt | self.llm
                    return await chain.ainvoke({
                        "age": user_profile.get("age", "N/A"),
                        "income": user_profile.get("income", 0),
                        "risk_tolerance": user_profile.get("risk_tolerance", "moderate"),
                        "investment_goal": user_profile.get("investment_goal", "long-term growth"),
                        "investment_horizon": user_profile.get("investment_horizon", "long-term"),
                        "current_portfolio": json.dumps(current_portfolio) if current_portfolio else "No current portfolio data"
                    })
                
                response = await traced_llm_call()
            else:
                chain = prompt | self.llm
                response = await chain.ainvoke({
                    "age": user_profile.get("age", "N/A"),
                    "income": user_profile.get("income", 0),
                    "risk_tolerance": user_profile.get("risk_tolerance", "moderate"),
                    "investment_goal": user_profile.get("investment_goal", "long-term growth"),
                    "investment_horizon": user_profile.get("investment_horizon", "long-term"),
                    "current_portfolio": json.dumps(current_portfolio) if current_portfolio else "No current portfolio data"
                })
            
            result = {
                "risk_assessment": response.content,
                "user_profile": user_profile,
                "source": "openai_gpt4_real_api",
                "timestamp": datetime.now().isoformat(),
                "api_call_successful": True
            }
            
            logger.info("✅ SUCCESS: OpenAI risk assessment completed")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in OpenAI risk assessment: {str(e)}")
            raise
    
    async def _real_generate_market_insights(self, market_data: Dict[str, Any], symbol: str = "SPY", period: str = "1d", analysis_focus: str = "comprehensive") -> Dict[str, Any]:
        """Real market insights using OpenAI API"""
        prompt = ChatPromptTemplate.from_template(
            """As a market analyst, provide insights on this market data:

Primary Symbol: {symbol}
Time Period: {period}
Analysis Focus: {analysis_focus}

Market Data: {market_data}

Provide comprehensive market insights including:
1. Current market conditions analysis
2. Key trends and patterns
3. Potential opportunities and risks
4. Short-term and long-term outlook
5. Actionable investment implications

Base your analysis on the actual market data provided."""
        )
        
        try:
            chain = prompt | self.llm
            response = await chain.ainvoke({
                "symbol": symbol,
                "period": period,
                "analysis_focus": analysis_focus,
                "market_data": json.dumps(market_data)
            })
            
            result = {
                "market_insights": response.content,
                "symbol": symbol,
                "period": period,
                "analysis_focus": analysis_focus,
                "source": "openai_gpt4_real_api",
                "timestamp": datetime.now().isoformat(),
                "api_call_successful": True
            }
            
            logger.info(f"✅ SUCCESS: OpenAI market insights generated for {symbol}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error generating market insights: {str(e)}")
            raise
    
    async def _real_generate_investment_proposal(self, user_profile: Dict[str, Any], portfolio_allocation: Dict[str, Any], market_conditions: Dict[str, Any] = None, proposal_type: str = "initial") -> Dict[str, Any]:
        """Real investment proposal using OpenAI API"""
        prompt = ChatPromptTemplate.from_template(
            """As a certified financial planner, create an investment proposal:

User Profile:
- Age: {age}
- Income: ${income:,}
- Risk Tolerance: {risk_tolerance}
- Investment Goal: {investment_goal}
- Investment Horizon: {investment_horizon}

Recommended Portfolio Allocation: {portfolio_allocation}
Market Conditions: {market_conditions}
Proposal Type: {proposal_type}

Create a detailed investment proposal including:
1. Executive summary of recommendations
2. Specific investment vehicles and allocations
3. Implementation timeline and steps
4. Expected returns and risks
5. Monitoring and rebalancing strategy
6. Next actions for the investor

Make it actionable and specific to their profile and current market conditions."""
        )
        
        try:
            chain = prompt | self.llm
            response = await chain.ainvoke({
                "age": user_profile.get("age", "N/A"),
                "income": user_profile.get("income", 0),
                "risk_tolerance": user_profile.get("risk_tolerance", "moderate"),
                "investment_goal": user_profile.get("investment_goal", "long-term growth"),
                "investment_horizon": user_profile.get("investment_horizon", "long-term"),
                "portfolio_allocation": json.dumps(portfolio_allocation),
                "market_conditions": json.dumps(market_conditions) if market_conditions else "Current market conditions",
                "proposal_type": proposal_type
            })
            
            result = {
                "investment_proposal": response.content,
                "user_profile": user_profile,
                "portfolio_allocation": portfolio_allocation,
                "proposal_type": proposal_type,
                "source": "openai_gpt4_real_api",
                "timestamp": datetime.now().isoformat(),
                "api_call_successful": True
            }
            
            logger.info("✅ SUCCESS: OpenAI investment proposal generated")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error generating investment proposal: {str(e)}")
            raise
    
    def get_available_tools(self) -> Dict[str, Any]:
        """Get list of available tools with real API integration status"""
        return self.available_tools
    
    async def shutdown(self):
        """Cleanup MCP client resources"""
        self.connected = False
        logger.info("🛑 MCP Client with real API integration shut down")

# Global MCP client instance
mcp_client = MCPClient() 