"""
Market Data MCP Server
Provides standardized access to Alpha Vantage and Yahoo Finance APIs
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import aiohttp
import yfinance as yf
from mcp.server import Server
from mcp.types import (
    Tool, 
    TextContent, 
    CallToolResult,
    ListToolsResult
)
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketDataMCPServer:
    """MCP Server for market data operations"""
    
    def __init__(self):
        self.alpha_vantage_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        self.alpha_vantage_url = "https://www.alphavantage.co/query"
        
        if not self.alpha_vantage_key:
            logger.warning("ALPHA_VANTAGE_API_KEY not set. Alpha Vantage features will be limited.")
        
        # Initialize MCP server
        self.server = Server("market-data-server")
        self._register_tools()
    
    def _register_tools(self):
        """Register all available tools"""
        
        @self.server.list_tools()
        async def list_tools() -> ListToolsResult:
            """List all available market data tools"""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="get_stock_quote",
                        description="Get real-time stock quote for a symbol",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "symbol": {
                                    "type": "string",
                                    "description": "Stock symbol (e.g., AAPL, SPY)"
                                },
                                "source": {
                                    "type": "string",
                                    "enum": ["alpha_vantage", "yahoo"],
                                    "description": "Data source to use",
                                    "default": "alpha_vantage"
                                }
                            },
                            "required": ["symbol"]
                        }
                    ),
                    Tool(
                        name="get_historical_data",
                        description="Get historical market data for a symbol",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "symbol": {
                                    "type": "string",
                                    "description": "Stock symbol"
                                },
                                "period": {
                                    "type": "string",
                                    "enum": ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"],
                                    "description": "Time period for historical data",
                                    "default": "1d"
                                },
                                "interval": {
                                    "type": "string",
                                    "enum": ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"],
                                    "description": "Data interval",
                                    "default": "1h"
                                }
                            },
                            "required": ["symbol"]
                        }
                    ),
                    Tool(
                        name="get_market_indices",
                        description="Get data for major market indices",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "source": {
                                    "type": "string",
                                    "enum": ["alpha_vantage", "yahoo"],
                                    "description": "Data source to use",
                                    "default": "yahoo"
                                }
                            }
                        }
                    ),
                    Tool(
                        name="get_market_summary",
                        description="Get comprehensive market summary with sentiment analysis",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "symbols": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "List of symbols to analyze",
                                    "default": ["SPY"]
                                }
                            }
                        }
                    )
                ]
            )
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Handle tool calls"""
            try:
                if name == "get_stock_quote":
                    result = await self._get_stock_quote(**arguments)
                elif name == "get_historical_data":
                    result = await self._get_historical_data(**arguments)
                elif name == "get_market_indices":
                    result = await self._get_market_indices(**arguments)
                elif name == "get_market_summary":
                    result = await self._get_market_summary(**arguments)
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
    
    async def _get_stock_quote(self, symbol: str, source: str = "alpha_vantage") -> Dict[str, Any]:
        """Get stock quote from specified source"""
        if source == "alpha_vantage" and self.alpha_vantage_key:
            return await self._get_alpha_vantage_quote(symbol)
        else:
            return await self._get_yahoo_quote(symbol)
    
    async def _get_alpha_vantage_quote(self, symbol: str) -> Dict[str, Any]:
        """Get stock quote from Alpha Vantage"""
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": self.alpha_vantage_key
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.alpha_vantage_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if "Global Quote" in data:
                            quote = data["Global Quote"]
                            return {
                                "symbol": symbol,
                                "source": "alpha_vantage",
                                "price": float(quote.get("05. price", 0)),
                                "change": float(quote.get("09. change", 0)),
                                "change_percent": float(quote.get("10. change percent", "0%").strip("%")),
                                "volume": int(quote.get("06. volume", 0)),
                                "high": float(quote.get("03. high", 0)),
                                "low": float(quote.get("04. low", 0)),
                                "open": float(quote.get("02. open", 0)),
                                "previous_close": float(quote.get("08. previous close", 0)),
                                "timestamp": datetime.now().isoformat()
                            }
                        else:
                            raise ValueError(f"Invalid response from Alpha Vantage: {data}")
                    else:
                        raise ValueError(f"Alpha Vantage API returned status {response.status}")
                        
        except Exception as e:
            logger.error(f"Alpha Vantage error for {symbol}: {str(e)}")
            # Fallback to Yahoo Finance
            return await self._get_yahoo_quote(symbol)
    
    async def _get_yahoo_quote(self, symbol: str) -> Dict[str, Any]:
        """Get stock quote from Yahoo Finance"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            hist = stock.history(period="2d", interval="1d")
            
            if hist.empty:
                raise ValueError(f"No data found for {symbol}")
            
            latest = hist.iloc[-1]
            current_price = latest["Close"]
            
            # Calculate change from previous day if available
            change = 0
            change_percent = 0
            if len(hist) >= 2:
                previous = hist.iloc[-2]["Close"]
                change = current_price - previous
                change_percent = (change / previous) * 100
            
            return {
                "symbol": symbol,
                "source": "yahoo",
                "price": float(current_price),
                "change": float(change),
                "change_percent": float(change_percent),
                "volume": int(latest["Volume"]),
                "high": float(latest["High"]),
                "low": float(latest["Low"]),
                "open": float(latest["Open"]),
                "previous_close": float(hist.iloc[-2]["Close"] if len(hist) >= 2 else latest["Open"]),
                "timestamp": datetime.now().isoformat(),
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "dividend_yield": info.get("dividendYield")
            }
            
        except Exception as e:
            logger.error(f"Yahoo Finance error for {symbol}: {str(e)}")
            raise ValueError(f"Failed to get quote for {symbol}: {str(e)}")
    
    async def _get_historical_data(self, symbol: str, period: str = "1d", interval: str = "1h") -> Dict[str, Any]:
        """Get historical data using Yahoo Finance"""
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period=period, interval=interval)
            
            if hist.empty:
                raise ValueError(f"No historical data found for {symbol}")
            
            # Convert DataFrame to dict format
            data_points = []
            for index, row in hist.iterrows():
                data_points.append({
                    "timestamp": index.isoformat(),
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": int(row["Volume"])
                })
            
            # Calculate period metrics
            first_price = hist.iloc[0]["Close"]
            last_price = hist.iloc[-1]["Close"]
            period_change = last_price - first_price
            period_change_percent = (period_change / first_price) * 100
            
            return {
                "symbol": symbol,
                "period": period,
                "interval": interval,
                "data_points": data_points,
                "summary": {
                    "first_price": float(first_price),
                    "last_price": float(last_price),
                    "period_change": float(period_change),
                    "period_change_percent": float(period_change_percent),
                    "high": float(hist["High"].max()),
                    "low": float(hist["Low"].min()),
                    "volume_avg": float(hist["Volume"].mean()),
                    "volatility": float(hist["Close"].pct_change().std() * 100)
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Historical data error for {symbol}: {str(e)}")
            raise ValueError(f"Failed to get historical data for {symbol}: {str(e)}")
    
    async def _get_market_indices(self, source: str = "yahoo") -> Dict[str, Any]:
        """Get major market indices data"""
        indices = {
            "S&P 500": "^GSPC",
            "Dow Jones": "^DJI", 
            "Nasdaq": "^IXIC",
            "VIX": "^VIX",
            "Gold": "GC=F",
            "Oil": "CL=F"
        }
        
        results = {}
        
        for name, symbol in indices.items():
            try:
                if source == "alpha_vantage" and self.alpha_vantage_key:
                    quote_data = await self._get_alpha_vantage_quote(symbol)
                else:
                    quote_data = await self._get_yahoo_quote(symbol)
                
                results[name] = quote_data
                
            except Exception as e:
                logger.warning(f"Failed to get data for {name} ({symbol}): {str(e)}")
                results[name] = {"error": str(e)}
        
        return {
            "indices": results,
            "timestamp": datetime.now().isoformat(),
            "source": source
        }
    
    async def _get_market_summary(self, symbols: List[str] = None) -> Dict[str, Any]:
        """Get comprehensive market summary"""
        if not symbols:
            symbols = ["SPY"]  # Default to S&P 500 ETF
        
        summary = {
            "symbols": {},
            "market_sentiment": "Neutral",
            "timestamp": datetime.now().isoformat()
        }
        
        # Get data for each symbol
        for symbol in symbols:
            try:
                quote_data = await self._get_stock_quote(symbol, "yahoo")
                summary["symbols"][symbol] = quote_data
            except Exception as e:
                logger.warning(f"Failed to get summary data for {symbol}: {str(e)}")
                summary["symbols"][symbol] = {"error": str(e)}
        
        # Calculate overall market sentiment
        try:
            spy_data = summary["symbols"].get("SPY", {})
            if "change_percent" in spy_data:
                change_percent = spy_data["change_percent"]
                if change_percent > 1:
                    summary["market_sentiment"] = "Strongly Positive"
                elif change_percent > 0:
                    summary["market_sentiment"] = "Slightly Positive" 
                elif change_percent > -1:
                    summary["market_sentiment"] = "Slightly Negative"
                else:
                    summary["market_sentiment"] = "Strongly Negative"
        except Exception as e:
            logger.warning(f"Failed to calculate market sentiment: {str(e)}")
        
        return summary

# Server instance
market_data_server = MarketDataMCPServer()

async def main():
    """Run the MCP server"""
    # Import here to avoid circular imports
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await market_data_server.server.run(
            read_stream, 
            write_stream,
            market_data_server.server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main()) 