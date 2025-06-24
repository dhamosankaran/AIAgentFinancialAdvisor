"""
Market Data Service for fetching and processing financial data
"""

import asyncio
from typing import Dict, List, Optional
import aiohttp
import yfinance as yf
from datetime import datetime, timedelta
import logging
from functools import lru_cache

from src.config.settings import settings

logger = logging.getLogger(__name__)

class MarketDataService:
    """Service for fetching and processing market data from multiple sources"""
    
    def __init__(self):
        self.alpha_vantage_key = settings.ALPHA_VANTAGE_API_KEY
        self.alpha_vantage_url = settings.ALPHA_VANTAGE_BASE_URL
        if not self.alpha_vantage_key:
            logger.warning("ALPHA_VANTAGE_API_KEY not set. Alpha Vantage features will be disabled.")
    
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
        """Get market data from Alpha Vantage"""
        if not self.alpha_vantage_key:
            logger.warning("Alpha Vantage API key not configured, falling back to Yahoo Finance")
            return await self._get_market_data_from_yahoo(symbols)
        
        if not symbols:
            symbols = ["SPY"]  # Default to S&P 500 ETF
        
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
    
    async def _get_market_data_from_yahoo(self, symbols: List[str] = None) -> Dict:
        """Get market data from Yahoo Finance as fallback"""
        if not symbols:
            symbols = ["SPY"]
        
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
        """Get a summary of market conditions"""
        try:
            # Get data from both sources
            alpha_data = await self.get_market_data()
            spy_data = await self.get_stock_data("SPY")
            
            # Combine and analyze data
            summary = {
                "timestamp": datetime.now().isoformat(),
                "sources": {
                    "alpha_vantage": alpha_data,
                    "yahoo_finance": spy_data
                },
                "market_sentiment": self._calculate_market_sentiment(alpha_data, spy_data)
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating market summary: {str(e)}")
            return {"error": str(e)}
    
    def _calculate_market_sentiment(self, alpha_data: Dict, yahoo_data: Dict) -> str:
        """Calculate overall market sentiment based on multiple data points"""
        try:
            # Try to get data from either source
            spy_change = 0
            
            # Try Alpha Vantage first
            if isinstance(alpha_data, dict) and "SPY" in alpha_data:
                spy_change = alpha_data["SPY"].get("change_percent", 0)
            # Fall back to Yahoo Finance
            elif isinstance(yahoo_data, dict) and "change_percent" in yahoo_data:
                spy_change = yahoo_data["change_percent"]
            
            # Determine sentiment
            if spy_change > 1:
                return "Strongly Positive"
            elif spy_change > 0:
                return "Slightly Positive"
            elif spy_change > -1:
                return "Slightly Negative"
            else:
                return "Strongly Negative"
                
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