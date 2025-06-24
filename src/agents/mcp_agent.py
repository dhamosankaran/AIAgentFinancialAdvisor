"""
MCP-Enabled Agent Base Class
Provides standardized tool calling via MCP servers
"""

import logging
from typing import Dict, List, Optional, Any
from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain.memory import ConversationBufferMemory
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.runnables import RunnablePassthrough

from src.mcp_clients.mcp_client import mcp_client
from .base_agent import BaseFinancialAgent

logger = logging.getLogger(__name__)

class MCPEnabledAgent(BaseFinancialAgent):
    """Base class for MCP-enabled financial advisor agents"""
    
    def __init__(
        self,
        llm: Optional[ChatOpenAI] = None,
        system_prompt: Optional[str] = None,
        memory: Optional[ConversationBufferMemory] = None,
        use_mcp: bool = True,
        mcp_tool_categories: List[str] = None
    ):
        """Initialize MCP-enabled agent"""
        self.use_mcp = use_mcp
        self.mcp_tool_categories = mcp_tool_categories or []
        self.mcp_tools = []
        
        # Initialize MCP tools if enabled
        if self.use_mcp:
            self._setup_mcp_tools()
        
        # Initialize base agent with MCP tools
        super().__init__(
            llm=llm,
            tools=self.mcp_tools,
            system_prompt=system_prompt,
            memory=memory
        )
    
    def _setup_mcp_tools(self):
        """Setup MCP tools for this agent"""
        try:
            # Get available tools from MCP client
            available_tools = mcp_client.get_available_tools()
            
            # Create LangChain tools from MCP tools
            for category in self.mcp_tool_categories:
                if category in available_tools:
                    for tool_name, tool_info in available_tools[category].items():
                        # Create a wrapper function for the MCP tool
                        mcp_tool = self._create_mcp_tool_wrapper(tool_name, tool_info, category)
                        self.mcp_tools.append(mcp_tool)
            
            logger.info(f"Initialized {len(self.mcp_tools)} MCP tools for agent")
            
        except Exception as e:
            logger.warning(f"Failed to setup MCP tools, falling back to direct tools: {str(e)}")
            self.use_mcp = False
    
    def _create_mcp_tool_wrapper(self, tool_name: str, tool_info: Dict, category: str) -> Tool:
        """Create a LangChain tool wrapper for an MCP tool"""
        async def mcp_tool_function(query: str = "", **kwargs) -> str:
            """Wrapper function for MCP tool calls"""
            try:
                # Initialize MCP client if needed
                if not mcp_client.connected:
                    await mcp_client.initialize()
                
                # Prepare arguments from kwargs or query
                arguments = kwargs.copy()
                if query and not arguments:
                    # Try to extract symbol from query for market data tools
                    if "symbol" in tool_info.get("inputSchema", {}).get("properties", {}):
                        # Simple extraction - in a real implementation, use NLP
                        words = query.upper().split()
                        for word in words:
                            if len(word) <= 5 and word.isalpha():
                                arguments["symbol"] = word
                                break
                        if "symbol" not in arguments:
                            arguments["symbol"] = "SPY"  # Default
                
                # Call MCP tool
                result = await mcp_client.call_tool(
                    tool_name, 
                    arguments, 
                    server_type=category
                )
                
                # Format result for LangChain
                if isinstance(result, dict):
                    if "error" in result:
                        return f"Error: {result['error']}"
                    else:
                        # Format based on tool type
                        if tool_name == "get_stock_quote":
                            symbol = result.get("symbol", "Unknown")
                            price = result.get("price", 0)
                            change = result.get("change", 0)
                            change_percent = result.get("change_percent", 0)
                            return f"{symbol}: ${price:.2f} ({change:+.2f}, {change_percent:+.2f}%)"
                        
                        elif tool_name == "analyze_portfolio":
                            allocation = result.get("portfolio_allocation", {})
                            analysis = result.get("analysis_result", "No analysis available")
                            return f"Portfolio Analysis: {allocation}\n\nAnalysis: {analysis}"
                        
                        else:
                            return str(result)
                else:
                    return str(result)
                    
            except Exception as e:
                error_msg = f"MCP tool error for {tool_name}: {str(e)}"
                logger.error(error_msg)
                return error_msg
        
        return Tool(
            name=tool_name,
            func=mcp_tool_function,
            description=tool_info.get("description", f"MCP tool: {tool_name}")
        )
    
    async def get_mcp_tool_result(self, tool_name: str, arguments: Dict[str, Any], category: str = None) -> Dict[str, Any]:
        """Direct MCP tool call for complex operations"""
        try:
            if not mcp_client.connected:
                await mcp_client.initialize()
            
            return await mcp_client.call_tool(tool_name, arguments, server_type=category)
            
        except Exception as e:
            logger.error(f"Direct MCP tool call failed: {str(e)}")
            raise

class MCPMarketAnalysisAgent(MCPEnabledAgent):
    """MCP-enabled market analysis agent"""
    
    def __init__(self):
        system_prompt = """You are a market analysis expert using advanced MCP tools. Your role is to:
        1. Analyze market conditions and trends using real-time data
        2. Provide insights on market movements and sentiment
        3. Use MCP tools to access reliable market data
        4. Offer data-driven market analysis and recommendations
        
        You have access to MCP tools for getting stock quotes, historical data, and market summaries.
        Always use the most current data available."""
        
        super().__init__(
            system_prompt=system_prompt,
            mcp_tool_categories=["market_data"]
        )

class MCPPortfolioAgent(MCPEnabledAgent):
    """MCP-enabled portfolio analysis agent"""
    
    def __init__(self):
        system_prompt = """You are a portfolio analysis expert using advanced MCP tools. Your role is to:
        1. Generate optimal portfolio allocations based on user profiles
        2. Perform comprehensive risk assessments
        3. Create actionable investment proposals
        4. Use MCP tools for AI-powered analysis
        
        You have access to MCP tools for portfolio analysis, risk assessment, and investment proposals.
        Always provide specific, actionable recommendations."""
        
        super().__init__(
            system_prompt=system_prompt,
            mcp_tool_categories=["ai_analysis", "market_data"]
        ) 