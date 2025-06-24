#!/usr/bin/env python3
"""
Test script for MCP integration in AgenticAI
Demonstrates the enhanced capabilities with Model Context Protocol
"""

import asyncio
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_mcp_client():
    """Test the MCP client functionality"""
    logger.info("Testing MCP Client...")
    
    try:
        from src.mcp_clients.mcp_client import mcp_client
        
        # Initialize MCP client
        await mcp_client.initialize()
        
        # Test tool discovery
        tools = mcp_client.get_available_tools()
        logger.info(f"Available MCP tool categories: {list(tools.keys())}")
        
        # Test market data tools
        logger.info("\n--- Testing Market Data Tools ---")
        
        # Test stock quote
        quote_result = await mcp_client.call_tool(
            "get_stock_quote",
            {"symbol": "AAPL", "source": "yahoo"},
            server_type="market_data"
        )
        logger.info(f"Stock quote result: {json.dumps(quote_result, indent=2, default=str)}")
        
        # Test market summary
        summary_result = await mcp_client.call_tool(
            "get_market_summary",
            {"symbols": ["SPY", "QQQ"]},
            server_type="market_data"
        )
        logger.info(f"Market summary result: {json.dumps(summary_result, indent=2, default=str)}")
        
        # Test AI analysis tools
        logger.info("\n--- Testing AI Analysis Tools ---")
        
        user_profile = {
            "name": "Test User",
            "age": 35,
            "income": 75000,
            "risk_tolerance": "Moderate",
            "investment_goal": "Retirement",
            "investment_horizon": "Long-term"
        }
        
        # Test portfolio analysis
        portfolio_result = await mcp_client.call_tool(
            "analyze_portfolio",
            {
                "user_profile": user_profile,
                "analysis_type": "comprehensive"
            },
            server_type="ai_analysis"
        )
        logger.info(f"Portfolio analysis result: {json.dumps(portfolio_result, indent=2, default=str)}")
        
        logger.info("\n--- MCP Client Test Completed Successfully ---")
        
    except Exception as e:
        logger.error(f"MCP Client test failed: {str(e)}")
        raise

async def test_mcp_market_data_service():
    """Test the enhanced MarketDataService with MCP"""
    logger.info("\nTesting Enhanced MarketDataService...")
    
    try:
        from src.services.market_data_service import MarketDataService
        
        # Test with MCP enabled
        market_service_mcp = MarketDataService(use_mcp=True)
        
        # Test market data retrieval
        symbols = ["AAPL", "GOOGL", "MSFT"]
        market_data = await market_service_mcp.get_market_data(symbols)
        
        logger.info(f"Market data via MCP: {json.dumps(market_data, indent=2, default=str)}")
        
        # Test with MCP disabled (fallback)
        market_service_direct = MarketDataService(use_mcp=False)
        market_data_direct = await market_service_direct.get_market_data(["SPY"])
        
        logger.info(f"Market data via direct API: {json.dumps(market_data_direct, indent=2, default=str)}")
        
        logger.info("\n--- MarketDataService Test Completed Successfully ---")
        
    except Exception as e:
        logger.error(f"MarketDataService test failed: {str(e)}")
        raise

async def test_mcp_agents():
    """Test MCP-enabled agents"""
    logger.info("\nTesting MCP-Enabled Agents...")
    
    try:
        from src.agents.mcp_agent import MCPMarketAnalysisAgent, MCPPortfolioAgent
        
        # Test Market Analysis Agent
        logger.info("\n--- Testing MCP Market Analysis Agent ---")
        market_agent = MCPMarketAnalysisAgent()
        
        market_response = await market_agent.process_message(
            "What's the current price of Apple stock and market sentiment?"
        )
        logger.info(f"Market agent response: {market_response}")
        
        # Test Portfolio Agent
        logger.info("\n--- Testing MCP Portfolio Agent ---")
        portfolio_agent = MCPPortfolioAgent()
        
        portfolio_response = await portfolio_agent.process_message(
            "Generate a portfolio allocation for a 30-year-old with moderate risk tolerance and $100k income"
        )
        logger.info(f"Portfolio agent response: {portfolio_response}")
        
        logger.info("\n--- MCP Agents Test Completed Successfully ---")
        
    except Exception as e:
        logger.error(f"MCP Agents test failed: {str(e)}")
        raise

async def performance_comparison():
    """Compare performance between MCP and direct API calls"""
    logger.info("\nPerformance Comparison: MCP vs Direct API...")
    
    try:
        from src.services.market_data_service import MarketDataService
        import time
        
        symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
        
        # Test MCP performance
        start_time = time.time()
        market_service_mcp = MarketDataService(use_mcp=True)
        mcp_data = await market_service_mcp.get_market_data(symbols)
        mcp_time = time.time() - start_time
        
        # Test direct API performance
        start_time = time.time()
        market_service_direct = MarketDataService(use_mcp=False)
        direct_data = await market_service_direct.get_market_data(symbols)
        direct_time = time.time() - start_time
        
        logger.info(f"MCP call time: {mcp_time:.2f} seconds")
        logger.info(f"Direct API call time: {direct_time:.2f} seconds")
        logger.info(f"Performance difference: {((direct_time - mcp_time) / direct_time * 100):+.1f}%")
        
        logger.info("\n--- Performance Comparison Completed ---")
        
    except Exception as e:
        logger.error(f"Performance comparison failed: {str(e)}")
        raise

async def main():
    """Main test function"""
    logger.info("=== AgenticAI MCP Integration Test Suite ===")
    logger.info(f"Test started at: {datetime.now().isoformat()}")
    
    try:
        # Run all tests
        await test_mcp_client()
        await test_mcp_market_data_service()
        await test_mcp_agents()
        await performance_comparison()
        
        logger.info("\n🎉 All MCP integration tests completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Test suite failed: {str(e)}")
        raise
    
    finally:
        # Cleanup
        try:
            from src.mcp_clients.mcp_client import mcp_client
            await mcp_client.shutdown()
        except:
            pass

if __name__ == "__main__":
    asyncio.run(main()) 