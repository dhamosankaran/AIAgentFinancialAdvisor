"""
Market Data Service for fetching and processing financial data
Enhanced with MCP integration for standardized tool calling
"""

import asyncio
from typing import Dict, List, Optional
import aiohttp
import yfinance as yf
from datetime import datetime, timedelta
import logging
from functools import lru_cache

from src.config.settings import settings
from src.mcp_clients.mcp_client import mcp_client

logger = logging.getLogger(__name__)

class MarketDataService:
    """Service for fetching and processing market data from multiple sources"""
    
    def __init__(self, use_mcp: bool = True):
        self.use_mcp = use_mcp
        self.alpha_vantage_key = settings.ALPHA_VANTAGE_API_KEY
        self.alpha_vantage_url = settings.ALPHA_VANTAGE_BASE_URL
        if not self.alpha_vantage_key:
            logger.warning("ALPHA_VANTAGE_API_KEY not set. Alpha Vantage features will be disabled.")
        
        # Initialize MCP client if enabled
        if self.use_mcp:
            self._initialize_mcp()
    
    def _initialize_mcp(self):
        """Initialize MCP client for external API calls"""
        try:
            # Check if MCP client is already initialized
            if not mcp_client.connected:
                logger.info("Initializing MCP client for market data service...")
                # Note: In a real implementation, you'd await this
                # For now, we'll set up a flag to initialize it when needed
                self.mcp_initialized = False
            else:
                self.mcp_initialized = True
                logger.info("MCP client already connected")
        except Exception as e:
            logger.warning(f"MCP initialization failed, falling back to direct API calls: {str(e)}")
            self.use_mcp = False
    
    async def get_stock_data(self, symbol: str, period: str = "1d") -> Dict:
        """Get stock data from Yahoo Finance"""
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period=period)
            
            if hist.empty:
                return {"error": f"No data found for {symbol}"}
            
            # Get the latest data
            latest = hist.iloc[-1]
            
            return {
                "symbol": symbol,
                "price": latest["Close"],
                "change": latest["Close"] - latest["Open"],
                "change_percent": ((latest["Close"] - latest["Open"]) / latest["Open"]) * 100,
                "volume": latest["Volume"],
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error fetching stock data for {symbol}: {str(e)}")
            return {"error": str(e)}
    
    async def get_market_data(self, symbols: List[str] = None) -> Dict:
        """Get market data using MCP or fallback to direct API calls"""
        if not symbols:
            symbols = ["^GSPC", "^IXIC", "^DJI", "^VIX"]  # Default to major indices for comprehensive sentiment
        
        # Try MCP first if enabled
        if self.use_mcp:
            try:
                return await self._get_market_data_via_mcp(symbols)
            except Exception as e:
                logger.warning(f"MCP market data call failed, falling back to direct API: {str(e)}")
                # Fall through to direct API calls
        
        # Fallback to original implementation
        if not self.alpha_vantage_key:
            logger.warning("Alpha Vantage API key not configured, falling back to Yahoo Finance")
            return await self._get_market_data_from_yahoo(symbols)
        
        try:
            async with aiohttp.ClientSession() as session:
                tasks = []
                for symbol in symbols:
                    params = {
                        "function": "GLOBAL_QUOTE",
                        "symbol": symbol,
                        "apikey": self.alpha_vantage_key
                    }
                    tasks.append(self._fetch_alpha_vantage(session, self.alpha_vantage_url, params))
                
                results = await asyncio.gather(*tasks)
                return self._process_market_data(results)
                
        except Exception as e:
            logger.error(f"Error fetching market data from Alpha Vantage: {str(e)}")
            logger.info("Falling back to Yahoo Finance data")
            return await self._get_market_data_from_yahoo(symbols)
    
    async def _get_market_data_via_mcp(self, symbols: List[str]) -> Dict:
        """Get market data via MCP client"""
        try:
            # Initialize MCP if needed
            if not mcp_client.connected:
                await mcp_client.initialize()
            
            # Get data for each symbol via MCP
            results = {}
            for symbol in symbols:
                try:
                    quote_data = await mcp_client.call_tool(
                        "get_stock_quote",
                        {"symbol": symbol, "source": "alpha_vantage"},
                        server_type="market_data"
                    )
                    
                    # Process MCP response
                    if "error" not in quote_data:
                        results[symbol] = {
                            "price": quote_data.get("price", 0),
                            "change": quote_data.get("change", 0),
                            "change_percent": quote_data.get("change_percent", 0),
                            "volume": quote_data.get("volume", 0),
                            "timestamp": quote_data.get("timestamp")
                        }
                    else:
                        logger.warning(f"MCP error for {symbol}: {quote_data['error']}")
                        
                except Exception as e:
                    logger.warning(f"MCP call failed for {symbol}: {str(e)}")
                    
            return results
            
        except Exception as e:
            logger.error(f"Error in MCP market data call: {str(e)}")
            raise
    
    async def _get_market_data_from_yahoo(self, symbols: List[str] = None) -> Dict:
        """Get market data from Yahoo Finance as fallback"""
        if not symbols:
            symbols = ["^GSPC", "^IXIC", "^DJI", "^VIX"]
        
        try:
            tasks = [self.get_stock_data(symbol) for symbol in symbols]
            results = await asyncio.gather(*tasks)
            
            processed_data = {}
            for result in results:
                if "error" not in result:
                    symbol = result["symbol"]
                    processed_data[symbol] = {
                        "price": result["price"],
                        "change": result["change"],
                        "change_percent": result["change_percent"],
                        "volume": result["volume"],
                        "timestamp": result["timestamp"]
                    }
            
            return processed_data
        except Exception as e:
            logger.error(f"Error fetching market data from Yahoo Finance: {str(e)}")
            return {"error": str(e)}
    
    async def _fetch_alpha_vantage(self, session: aiohttp.ClientSession, url: str, params: Dict) -> Dict:
        """Fetch data from Alpha Vantage API"""
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Alpha Vantage API request failed with status {response.status}")
                    return {"error": f"API request failed with status {response.status}"}
        except Exception as e:
            logger.error(f"Error in Alpha Vantage request: {str(e)}")
            return {"error": str(e)}
    
    def _process_market_data(self, results: List[Dict]) -> Dict:
        """Process and combine market data results"""
        processed_data = {}
        
        for result in results:
            if "error" in result:
                logger.warning(f"Error in market data result: {result['error']}")
                continue
                
            if "Global Quote" in result:
                quote = result["Global Quote"]
                symbol = quote.get("01. symbol")
                if symbol:
                    try:
                        processed_data[symbol] = {
                            "price": float(quote.get("05. price", 0)),
                            "change": float(quote.get("09. change", 0)),
                            "change_percent": float(quote.get("10. change percent", "0%").strip("%")),
                            "volume": int(quote.get("06. volume", 0)),
                            "timestamp": datetime.now().isoformat()
                        }
                    except (ValueError, TypeError) as e:
                        logger.error(f"Error processing market data for {symbol}: {str(e)}")
                        continue
        
        return processed_data
    
    async def get_market_summary(self) -> Dict:
        """Get a comprehensive summary of market conditions using multiple indices"""
        try:
            # Get data from major indices for comprehensive analysis
            major_indices = ["^GSPC", "^IXIC", "^DJI", "^VIX"]
            alpha_data = await self.get_market_data(major_indices)
            
            # Get additional market data including SPY as fallback
            spy_data = await self.get_stock_data("SPY")
            indices_data = await self.get_major_indices()
            
            # Combine and analyze data
            summary = {
                "timestamp": datetime.now().isoformat(),
                "major_indices": alpha_data,
                "market_indices": indices_data,
                "spy_fallback": spy_data,
                "market_sentiment": self._calculate_market_sentiment(alpha_data, spy_data),
                "analysis_method": "Multi-index comprehensive analysis (S&P 500, NASDAQ, Dow Jones, VIX)"
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating market summary: {str(e)}")
            return {"error": str(e)}
    
    def _calculate_market_sentiment(self, alpha_data: Dict, yahoo_data: Dict) -> str:
        """Calculate comprehensive market sentiment based on multiple indices"""
        try:
            sentiment_scores = []
            
            # Define major indices for sentiment analysis
            indices_data = {
                "^GSPC": "S&P 500",
                "^IXIC": "NASDAQ", 
                "^DJI": "Dow Jones",
                "^VIX": "VIX (Fear Index)"
            }
            
            # Check alpha_data first
            for symbol, name in indices_data.items():
                change_percent = 0
                
                # Try to get data from alpha_data first
                if isinstance(alpha_data, dict) and symbol in alpha_data:
                    change_percent = alpha_data[symbol].get("change_percent", 0)
                # Fallback: if it's SPY in yahoo_data, use that for general market
                elif symbol == "^GSPC" and isinstance(yahoo_data, dict) and "change_percent" in yahoo_data:
                    change_percent = yahoo_data["change_percent"]
                
                if change_percent != 0:
                    # VIX is inverse - higher VIX means more fear/bearish sentiment
                    if symbol == "^VIX":
                        if change_percent > 15:
                            sentiment_scores.append(-2)  # Very bearish
                        elif change_percent > 5:
                            sentiment_scores.append(-1)  # Bearish
                        elif change_percent < -15:
                            sentiment_scores.append(2)   # Very bullish
                        elif change_percent < -5:
                            sentiment_scores.append(1)   # Bullish
                        else:
                            sentiment_scores.append(0)   # Neutral
                    else:
                        # Regular indices - positive change is bullish
                        if change_percent > 2:
                            sentiment_scores.append(2)   # Very bullish
                        elif change_percent > 0.5:
                            sentiment_scores.append(1)   # Bullish
                        elif change_percent < -2:
                            sentiment_scores.append(-2)  # Very bearish
                        elif change_percent < -0.5:
                            sentiment_scores.append(-1)  # Bearish
                        else:
                            sentiment_scores.append(0)   # Neutral
            
            # If no data found, return neutral
            if not sentiment_scores:
                logger.warning("No market data found for sentiment calculation")
                return "Neutral"
            
            # Calculate weighted average sentiment
            avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
            
            # Map sentiment score to description
            if avg_sentiment >= 1.5:
                return "Very Bullish"
            elif avg_sentiment >= 0.5:
                return "Bullish"
            elif avg_sentiment <= -1.5:
                return "Very Bearish"
            elif avg_sentiment <= -0.5:
                return "Bearish"
            else:
                return "Neutral"
                
        except Exception as e:
            logger.error(f"Error calculating market sentiment: {str(e)}")
            return "Neutral"

    async def get_major_indices(self) -> List[Dict]:
        """Get data for major market indices, VIX, Gold, and Oil."""
        symbols = {
            "Dow": "^DJI",
            "S&P 500": "^GSPC",
            "Nasdaq": "^IXIC",
            "VIX": "^VIX",
            "Gold": "GC=F",
            "Oil": "CL=F",
        }
        
        tasks = [self.get_stock_data(symbol) for symbol in symbols.values()]
        results = await asyncio.gather(*tasks)
        
        # Map results back to names
        named_results = []
        for result in results:
            if "error" not in result:
                name = next((name for name, sym in symbols.items() if sym == result["symbol"]), None)
                if name:
                    result["name"] = name
                    named_results.append(result)

        return named_results

    async def get_historical_data(self, symbol: str, period: str = "1d", interval: str = "1h") -> Dict:
        """Get historical stock data from Yahoo Finance for a given period."""
        try:
            stock = yf.Ticker(symbol)
            # Adjust interval for longer periods
            if period in ["1y", "2y", "5y", "max"]:
                interval = "1d"
            elif period in ["1mo", "3mo", "6mo"]:
                 interval = "1d"
            elif period == "5d":
                interval = "15m"
            else: #1d
                interval = "5m"


            hist = stock.history(period=period, interval=interval)
            
            if hist.empty:
                return {"error": f"No historical data found for {symbol}"}
            
            hist.reset_index(inplace=True)
            # For intraday data, 'Datetime' is the column. For daily, it's 'Date'.
            date_column = 'Datetime' if 'Datetime' in hist.columns else 'Date'
            
            return {
                "symbol": symbol,
                "history": [
                    {"date": row[date_column].isoformat(), "price": row["Close"]}
                    for index, row in hist.iterrows()
                ]
            }
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {str(e)}")
            return {"error": str(e)} 