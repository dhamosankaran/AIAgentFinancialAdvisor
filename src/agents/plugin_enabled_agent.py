"""
Plugin-Enabled Agent
Financial agent with dynamic tool discovery and plugin support
"""

import logging
from typing import Dict, List, Optional, Any
from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool
from langchain.memory import ConversationBufferMemory

from .responsible_agent import ResponsibleFinancialAgent
from ..services.plugin_registry import plugin_registry, PluginCategory

class PluginEnabledAgent(ResponsibleFinancialAgent):
    """Financial agent with dynamic plugin and tool discovery"""
    
    def __init__(
        self,
        llm: Optional[ChatOpenAI] = None,
        system_prompt: Optional[str] = None,
        memory: Optional[ConversationBufferMemory] = None,
        plugin_categories: List[PluginCategory] = None,
        enable_plugin_discovery: bool = True,
        enable_responsible_ai: bool = True,
        **responsible_ai_kwargs
    ):
        """Initialize plugin-enabled agent"""
        self.plugin_categories = plugin_categories or []
        self.enable_plugin_discovery = enable_plugin_discovery
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize with empty tools first
        base_tools = []
        
        # Initialize ResponsibleFinancialAgent (which inherits from BaseFinancialAgent)
        super().__init__(
            llm=llm,
            tools=base_tools,
            system_prompt=system_prompt,
            memory=memory,
            **responsible_ai_kwargs if enable_responsible_ai else {}
        )
        
        # Discover and load plugin tools
        if self.enable_plugin_discovery:
            self._discover_and_load_plugin_tools()
    
    def _discover_and_load_plugin_tools(self):
        """Discover and load tools from plugins"""
        self.logger.info("Discovering plugin tools")
        
        try:
            # Get tools from plugin registry
            if self.plugin_categories:
                # Get tools for specific categories
                all_tools = []
                for category in self.plugin_categories:
                    category_tools = plugin_registry.get_available_tools(category)
                    all_tools.extend(category_tools)
                    self.logger.info(f"Found {len(category_tools)} tools for category {category.value}")
            else:
                # Get all available tools
                all_tools = plugin_registry.get_available_tools()
                self.logger.info(f"Found {len(all_tools)} total tools from all plugins")
            
            # Update agent tools
            self.tools.extend(all_tools)
            
            # Reinitialize agent with new tools
            self._initialize_agent()
            
            self.logger.info(f"Successfully loaded {len(all_tools)} plugin tools")
            
        except Exception as e:
            self.logger.error(f"Error discovering plugin tools: {str(e)}")
    
    async def refresh_plugin_tools(self):
        """Refresh tools from plugin registry (useful for runtime plugin updates)"""
        self.logger.info("Refreshing plugin tools")
        
        try:
            # Clear current plugin tools (keep only base tools)
            original_tool_count = len(self.tools)
            
            # Remove plugin tools (assuming they were added after base tools)
            # In a more sophisticated implementation, you'd track which tools are from plugins
            self.tools = []
            
            # Rediscover plugin tools
            self._discover_and_load_plugin_tools()
            
            new_tool_count = len(self.tools)
            self.logger.info(f"Tool refresh completed: {original_tool_count} -> {new_tool_count} tools")
            
        except Exception as e:
            self.logger.error(f"Error refreshing plugin tools: {str(e)}")
    
    def get_available_plugins(self) -> Dict[str, Any]:
        """Get information about available plugins"""
        return plugin_registry.get_all_plugins()
    
    def get_plugin_stats(self) -> Dict[str, Any]:
        """Get plugin statistics"""
        return plugin_registry.get_plugin_stats()
    
    async def load_plugin(self, plugin_name: str) -> bool:
        """Load a specific plugin and refresh tools"""
        success = await plugin_registry.load_plugin(plugin_name)
        if success:
            await self.refresh_plugin_tools()
        return success
    
    async def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a specific plugin and refresh tools"""
        success = await plugin_registry.unload_plugin(plugin_name)
        if success:
            await self.refresh_plugin_tools()
        return success
    
    def get_tool_manifest(self) -> Dict[str, Any]:
        """Get detailed information about available tools"""
        tool_manifest = {
            "total_tools": len(self.tools),
            "tools": [],
            "plugin_tools": [],
            "categories": {}
        }
        
        # Get plugin information
        plugins = plugin_registry.get_all_plugins()
        
        for tool in self.tools:
            tool_info = {
                "name": tool.name,
                "description": tool.description,
                "source": "unknown"
            }
            
            # Try to identify which plugin this tool came from
            for plugin_name, plugin_info in plugins.items():
                if any(p_tool.name == tool.name for p_tool in plugin_info.tools):
                    tool_info["source"] = plugin_name
                    tool_info["category"] = plugin_info.metadata.category.value
                    tool_manifest["plugin_tools"].append(tool_info)
                    
                    # Update category count
                    category = plugin_info.metadata.category.value
                    if category not in tool_manifest["categories"]:
                        tool_manifest["categories"][category] = 0
                    tool_manifest["categories"][category] += 1
                    break
            
            tool_manifest["tools"].append(tool_info)
        
        return tool_manifest

class DynamicFinancialAgent(PluginEnabledAgent):
    """
    Dynamic financial agent that automatically adapts tools based on context
    """
    
    def __init__(self, **kwargs):
        # Define default plugin categories for financial agents
        default_categories = [
            PluginCategory.MARKET_DATA,
            PluginCategory.AI_ANALYSIS,
            PluginCategory.RISK_ASSESSMENT,
            PluginCategory.PORTFOLIO_MANAGEMENT
        ]
        
        # Enhanced system prompt for dynamic agent
        default_system_prompt = """You are an advanced financial advisor agent with access to dynamic tools and plugins.
        
        You have access to various tools that can help you:
        1. Analyze market data and conditions
        2. Assess investment risks
        3. Generate portfolio recommendations
        4. Provide AI-powered financial insights
        
        When responding to user queries:
        - Use the most appropriate tools for the task
        - Explain your reasoning and methodology
        - Provide clear, actionable advice
        - Always include appropriate disclaimers
        - Consider the user's risk profile and investment goals
        
        Available tool categories: Market Data, AI Analysis, Risk Assessment, Portfolio Management
        
        Always aim to provide comprehensive, well-researched financial guidance while maintaining the highest standards of responsible AI practices."""
        
        # Remove plugin_categories and system_prompt from kwargs to avoid conflicts
        kwargs_copy = kwargs.copy()
        kwargs_copy.pop('plugin_categories', None)
        kwargs_copy.pop('system_prompt', None)
        
        super().__init__(
            plugin_categories=kwargs.get('plugin_categories', default_categories),
            system_prompt=kwargs.get('system_prompt', default_system_prompt),
            **kwargs_copy
        )
    
    async def process_message_with_context(self, message: str, context: Dict[str, Any] = None) -> str:
        """Process message with additional context for tool selection"""
        # In a more advanced implementation, you could:
        # 1. Analyze the message to determine which tools are most relevant
        # 2. Dynamically load/prioritize tools based on context
        # 3. Provide tool usage statistics and recommendations
        
        return await self.process_message(message)
    
    async def analyze_tool_usage(self) -> Dict[str, Any]:
        """Analyze tool usage patterns (placeholder for advanced implementation)"""
        return {
            "most_used_tools": [],
            "least_used_tools": [],
            "success_rate": 0.0,
            "average_response_time": 0.0,
            "recommendations": []
        } 