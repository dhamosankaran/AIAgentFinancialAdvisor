# MCP Integration in AgenticAI

## Overview

This document describes the Model Context Protocol (MCP) integration in the AgenticAI Financial Investment Advisor application. MCP provides a standardized way for AI applications to securely connect to external data sources and tools.

## Architecture

### Before MCP Integration
```
AgenticAI Application
├── MarketDataService ──HTTP──> Alpha Vantage API
├── BaseAgent ──LangChain──> OpenAI API  
└── MarketDataService ──yfinance──> Yahoo Finance
```

### After MCP Integration
```
AgenticAI Application
├── MCP Client ──JSON-RPC──> Market Data MCP Server ──> Alpha Vantage API
├── MCP Client ──JSON-RPC──> Market Data MCP Server ──> Yahoo Finance API
└── MCP Client ──JSON-RPC──> AI Analysis MCP Server ──> OpenAI API
```

## Components

### 1. MCP Servers

#### Market Data MCP Server (`src/mcp_servers/market_data_server.py`)
**Purpose**: Provides standardized access to financial market data

**Tools Available**:
- `get_stock_quote`: Real-time stock quotes
- `get_historical_data`: Historical market data
- `get_market_indices`: Major market indices data
- `get_market_summary`: Comprehensive market summary

**Data Sources**:
- Alpha Vantage API (primary)
- Yahoo Finance (fallback)

#### AI Analysis MCP Server (`src/mcp_servers/ai_analysis_server.py`)
**Purpose**: Provides standardized access to AI-powered financial analysis

**Tools Available**:
- `analyze_portfolio`: Generate portfolio analysis and recommendations
- `assess_risk`: Detailed risk assessment
- `generate_market_insights`: AI-powered market insights
- `generate_investment_proposal`: Investment proposals and recommendations

**AI Backend**: OpenAI GPT-4 Turbo

### 2. MCP Client (`src/mcp_clients/mcp_client.py`)

**Purpose**: Unified client for accessing MCP servers from AgenticAI application

**Features**:
- Automatic server discovery and connection
- Tool discovery and registration
- Graceful error handling and fallbacks
- Connection pooling and management

### 3. Enhanced Services

#### MarketDataService
- **MCP Integration**: Uses MCP client for data retrieval
- **Fallback Support**: Automatically falls back to direct API calls if MCP fails
- **Backward Compatibility**: Existing API unchanged

### 4. MCP-Enabled Agents

#### MCPEnabledAgent Base Class
- **Dynamic Tool Discovery**: Automatically discovers and registers MCP tools
- **Tool Wrapping**: Converts MCP tools to LangChain tools
- **Error Handling**: Robust error handling for MCP operations

#### Specialized Agents
- **MCPMarketAnalysisAgent**: Market analysis using MCP tools
- **MCPPortfolioAgent**: Portfolio analysis using MCP tools

## Benefits

### 1. **Enhanced Security**
- API keys isolated in MCP servers
- Reduced attack surface on main application
- Centralized credential management

### 2. **Improved Performance**
- Connection pooling in MCP servers
- Reduced API call overhead
- Intelligent caching strategies

### 3. **Better Maintainability**
- Standardized tool interfaces
- Centralized external API management
- Easier debugging and monitoring

### 4. **Increased Reliability**
- Automatic failover to backup data sources
- Graceful degradation when services unavailable
- Comprehensive error handling

## Installation and Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Variables
Ensure your `.env` file contains:
```
ALPHA_VANTAGE_API_KEY=your_api_key
OPENAI_API_KEY=your_openai_key
```

### 3. Test MCP Integration
```bash
python test_mcp_integration.py
```

## Usage Examples

### Using MCP Client Directly
```python
from src.mcp_clients.mcp_client import mcp_client

# Initialize MCP client
await mcp_client.initialize()

# Get stock quote
quote = await mcp_client.call_tool(
    "get_stock_quote", 
    {"symbol": "AAPL"}, 
    server_type="market_data"
)

# Generate portfolio analysis
analysis = await mcp_client.call_tool(
    "analyze_portfolio",
    {"user_profile": user_profile},
    server_type="ai_analysis"
)
```

### Using Enhanced MarketDataService
```python
from src.services.market_data_service import MarketDataService

# Create service with MCP enabled (default)
market_service = MarketDataService(use_mcp=True)

# Get market data (will use MCP if available, fallback to direct API)
data = await market_service.get_market_data(["AAPL", "GOOGL"])
```

### Using MCP-Enabled Agents
```python
from src.agents.mcp_agent import MCPMarketAnalysisAgent, MCPPortfolioAgent

# Create MCP-enabled agents
market_agent = MCPMarketAnalysisAgent()
portfolio_agent = MCPPortfolioAgent()

# Use agents with MCP tools
market_response = await market_agent.process_message(
    "What's the current price of Apple stock?"
)

portfolio_response = await portfolio_agent.process_message(
    "Generate a portfolio for a 30-year-old with moderate risk tolerance"
)
```

## Configuration

### Enabling/Disabling MCP
MCP integration can be controlled via constructor parameters:

```python
# Enable MCP (default)
service = MarketDataService(use_mcp=True)

# Disable MCP (use direct API calls)
service = MarketDataService(use_mcp=False)

# MCP-enabled agent
agent = MCPEnabledAgent(use_mcp=True, mcp_tool_categories=["market_data"])
```

## Testing

### Comprehensive Test Suite
Run the complete MCP integration test suite:
```bash
python test_mcp_integration.py
```

**Test Coverage**:
- MCP client functionality
- Tool discovery and calling
- Market data service integration
- Agent functionality
- Performance comparison
- Error handling and fallbacks

### Individual Component Tests
```bash
# Test MCP servers
python -m src.mcp_servers.market_data_server
python -m src.mcp_servers.ai_analysis_server

# Test agents
python -m pytest tests/ -k mcp
```

## Monitoring and Debugging

### Logging
MCP integration includes comprehensive logging:
- MCP client operations
- Tool discovery and calls
- Server connections and errors
- Performance metrics

### Error Handling
- Graceful fallback to direct API calls
- Detailed error logging
- User-friendly error messages
- Automatic retry mechanisms

## Development Guidelines

### Adding New MCP Tools

1. **Add to MCP Server**:
```python
@self.server.list_tools()
async def list_tools() -> ListToolsResult:
    tools.append(Tool(
        name="new_tool",
        description="Description of new tool",
        inputSchema={...}
    ))
```

2. **Implement Tool Logic**:
```python
async def _new_tool_implementation(self, **arguments):
    # Tool implementation
    return result
```

3. **Update Tool Calling Logic**:
```python
if name == "new_tool":
    result = await self._new_tool_implementation(**arguments)
```

### Best Practices

1. **Error Handling**: Always implement graceful fallbacks
2. **Logging**: Use appropriate log levels for debugging
3. **Testing**: Write tests for new tools and functionality
4. **Documentation**: Update this README when adding features
5. **Security**: Never expose API keys in client code

## Troubleshooting

### Common Issues

1. **MCP Client Not Connected**
   - Solution: Ensure `await mcp_client.initialize()` is called
   - Check: Server processes are running
   - Verify: Environment variables are set

2. **Tool Not Found**
   - Solution: Verify tool is registered in MCP server
   - Check: Tool category is included in agent configuration
   - Debug: Review tool discovery logs

3. **API Errors**
   - Solution: MCP will automatically fallback to direct APIs
   - Check: API keys are valid and not rate-limited
   - Monitor: Error logs for specific failure reasons

### Debug Mode
Enable debug logging for detailed troubleshooting:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

### Planned Features
1. **Real MCP Server Processes**: Replace simulation with actual MCP servers
2. **Advanced Caching**: Implement intelligent caching strategies
3. **Load Balancing**: Distribute requests across multiple server instances
4. **Monitoring Dashboard**: Real-time monitoring of MCP operations
5. **Custom Tool Plugins**: Plugin architecture for custom tools

### Performance Optimizations
1. **Connection Pooling**: Reuse connections across requests
2. **Parallel Processing**: Concurrent tool calls where possible
3. **Intelligent Routing**: Route requests to optimal servers
4. **Predictive Caching**: Cache likely-needed data in advance

## Contributing

When contributing to MCP integration:

1. Follow existing code patterns and conventions
2. Add comprehensive tests for new functionality
3. Update documentation for any API changes
4. Ensure backward compatibility where possible
5. Test both MCP and fallback code paths

## License

This MCP integration is part of the AgenticAI project and follows the same license terms. 