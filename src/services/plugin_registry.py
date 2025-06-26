"""
Plugin Registry Service
Enables dynamic tool discovery and plugin management for AgenticAI
"""

import os
import json
import logging
import importlib
import inspect
from typing import Dict, List, Optional, Any, Type, Callable
from datetime import datetime
from pathlib import Path
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import asyncio
from langchain_core.tools import Tool

class PluginStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    LOADING = "loading"

class PluginCategory(Enum):
    MARKET_DATA = "market_data"
    AI_ANALYSIS = "ai_analysis"
    RISK_ASSESSMENT = "risk_assessment"
    PORTFOLIO_MANAGEMENT = "portfolio_management"
    COMPLIANCE = "compliance"
    NOTIFICATIONS = "notifications"
    CUSTOM = "custom"

@dataclass
class PluginMetadata:
    name: str
    version: str
    description: str
    category: PluginCategory
    author: str
    dependencies: List[str]
    config_schema: Dict[str, Any]
    api_requirements: List[str]
    min_version: str = "1.0.0"

@dataclass
class PluginInfo:
    metadata: PluginMetadata
    status: PluginStatus
    tools: List[Tool]
    instance: Any
    load_time: datetime
    error_message: Optional[str] = None

class BasePlugin(ABC):
    """Base class for all AgenticAI plugins"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(f"plugin.{self.__class__.__name__}")
        self.status = PluginStatus.LOADING
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the plugin"""
        pass
    
    @abstractmethod
    def get_tools(self) -> List[Tool]:
        """Get available tools from this plugin"""
        pass
    
    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """Get plugin metadata"""
        pass
    
    async def cleanup(self):
        """Clean up resources when plugin is unloaded"""
        pass
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate plugin configuration"""
        return True

class PluginRegistry:
    """Registry for managing AgenticAI plugins"""
    
    def __init__(self, plugins_dir: str = "src/plugins"):
        self.plugins_dir = Path(plugins_dir)
        self.plugins: Dict[str, PluginInfo] = {}
        self.logger = logging.getLogger(__name__)
        
        # Create plugins directory if it doesn't exist
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        
        # Plugin configurations
        self.config_file = self.plugins_dir / "config.json"
        self.plugin_configs = self._load_plugin_configs()
    
    def _load_plugin_configs(self) -> Dict[str, Any]:
        """Load plugin configurations from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading plugin configs: {str(e)}")
        
        return {}
    
    def _save_plugin_configs(self):
        """Save plugin configurations to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.plugin_configs, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving plugin configs: {str(e)}")
    
    async def discover_plugins(self) -> List[str]:
        """Discover available plugins in the plugins directory"""
        self.logger.info("Starting plugin discovery")
        discovered_plugins = []
        
        if not self.plugins_dir.exists():
            self.logger.warning(f"Plugins directory {self.plugins_dir} does not exist")
            return discovered_plugins
        
        # Look for Python files in plugins directory
        for plugin_file in self.plugins_dir.glob("*.py"):
            if plugin_file.name.startswith("__"):
                continue
            
            plugin_name = plugin_file.stem
            discovered_plugins.append(plugin_name)
            self.logger.info(f"Discovered plugin: {plugin_name}")
        
        # Also discover MCP servers as plugins
        mcp_servers_dir = Path("src/mcp_servers")
        if mcp_servers_dir.exists():
            for mcp_file in mcp_servers_dir.glob("*_server.py"):
                if mcp_file.name.startswith("__"):
                    continue
                
                plugin_name = f"mcp_{mcp_file.stem}"
                discovered_plugins.append(plugin_name)
                self.logger.info(f"Discovered MCP plugin: {plugin_name}")
        
        self.logger.info(f"Plugin discovery completed. Found {len(discovered_plugins)} plugins")
        return discovered_plugins
    
    async def load_plugin(self, plugin_name: str) -> bool:
        """Load a specific plugin"""
        self.logger.info(f"Loading plugin: {plugin_name}")
        
        try:
            # Handle MCP plugins differently
            if plugin_name.startswith("mcp_"):
                return await self._load_mcp_plugin(plugin_name)
            
            # Load regular plugin
            return await self._load_regular_plugin(plugin_name)
            
        except Exception as e:
            self.logger.error(f"Error loading plugin {plugin_name}: {str(e)}")
            self.plugins[plugin_name] = PluginInfo(
                metadata=PluginMetadata("", "", "", PluginCategory.CUSTOM, "", [], {}, []),
                status=PluginStatus.ERROR,
                tools=[],
                instance=None,
                load_time=datetime.now(),
                error_message=str(e)
            )
            return False
    
    async def _load_regular_plugin(self, plugin_name: str) -> bool:
        """Load a regular plugin"""
        module_path = f"src.plugins.{plugin_name}"
        
        try:
            # Import the plugin module
            plugin_module = importlib.import_module(module_path)
            
            # Find plugin class
            plugin_class = None
            for name, obj in inspect.getmembers(plugin_module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, BasePlugin) and 
                    obj != BasePlugin):
                    plugin_class = obj
                    break
            
            if not plugin_class:
                raise ValueError(f"No valid plugin class found in {plugin_name}")
            
            # Get plugin config
            config = self.plugin_configs.get(plugin_name, {})
            
            # Create plugin instance
            plugin_instance = plugin_class(config)
            
            # Initialize plugin
            initialized = await plugin_instance.initialize()
            if not initialized:
                raise RuntimeError("Plugin initialization failed")
            
            # Get metadata and tools
            metadata = plugin_instance.get_metadata()
            tools = plugin_instance.get_tools()
            
            # Register plugin
            self.plugins[plugin_name] = PluginInfo(
                metadata=metadata,
                status=PluginStatus.ACTIVE,
                tools=tools,
                instance=plugin_instance,
                load_time=datetime.now()
            )
            
            self.logger.info(f"Successfully loaded plugin: {plugin_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading regular plugin {plugin_name}: {str(e)}")
            raise
    
    async def _load_mcp_plugin(self, plugin_name: str) -> bool:
        """Load an MCP server as a plugin"""
        # This is a wrapper for existing MCP servers
        server_name = plugin_name.replace("mcp_", "")
        
        try:
            # Import MCP client
            from src.mcp_clients.mcp_client import mcp_client
            
            # Initialize MCP client if not already done
            if not mcp_client.connected:
                await mcp_client.initialize()
            
            # Get available tools from MCP client for this server
            available_tools = mcp_client.get_available_tools()
            
            # Create LangChain tools for this MCP server
            tools = []
            server_type = None
            
            if "market_data" in server_name:
                server_type = "market_data"
                category = PluginCategory.MARKET_DATA
            elif "ai_analysis" in server_name:
                server_type = "ai_analysis"
                category = PluginCategory.AI_ANALYSIS
            else:
                server_type = "custom"
                category = PluginCategory.CUSTOM
            
            if server_type in available_tools:
                for tool_name, tool_info in available_tools[server_type].items():
                    # Create wrapper function for MCP tool (must be synchronous for LangChain)
                    def make_mcp_tool_func(tool_name_ref, server_type_ref):
                        def mcp_tool_func(query: str = "", **kwargs):
                            import asyncio
                            import json
                            
                            # Parse the query to extract proper parameters for AI analysis tools
                            arguments = kwargs.copy() if kwargs else {}
                            
                            if server_type_ref == "ai_analysis" and query:
                                # Try to parse query string for AI analysis tools
                                if tool_name_ref == "analyze_portfolio":
                                    # Create a basic user profile from the query
                                    arguments = {
                                        "user_profile": {
                                            "name": query.split(",")[0].strip() if "," in query else "User",
                                            "risk_tolerance": "moderate",
                                            "age": 35,
                                            "income": 75000,
                                            "investment_goal": "long-term growth",
                                            "investment_horizon": "long-term"
                                        },
                                        "analysis_type": "comprehensive"
                                    }
                                    # Extract risk tolerance from query if mentioned
                                    query_lower = query.lower()
                                    if "conservative" in query_lower:
                                        arguments["user_profile"]["risk_tolerance"] = "conservative"
                                    elif "aggressive" in query_lower:
                                        arguments["user_profile"]["risk_tolerance"] = "aggressive"
                                    elif "moderate" in query_lower:
                                        arguments["user_profile"]["risk_tolerance"] = "moderate"
                                        
                                elif tool_name_ref == "assess_risk":
                                    arguments = {
                                        "user_profile": {
                                            "name": query.split(",")[0].strip() if "," in query else "User",
                                            "risk_tolerance": "moderate",
                                            "age": 35,
                                            "income": 75000
                                        }
                                    }
                                elif tool_name_ref == "generate_market_insights":
                                    arguments = {
                                        "market_data": {"analysis_request": query},
                                        "symbol": "SPY",
                                        "analysis_focus": "comprehensive"
                                    }
                                elif tool_name_ref == "generate_investment_proposal":
                                    arguments = {
                                        "user_profile": {
                                            "name": query.split(",")[0].strip() if "," in query else "User",
                                            "risk_tolerance": "moderate",
                                            "age": 35,
                                            "income": 75000
                                        },
                                        "portfolio_allocation": {"stocks": 60, "bonds": 30, "cash": 10},
                                        "proposal_type": "initial"
                                    }
                            else:
                                # For market data tools, use the original approach
                                if not arguments:
                                    arguments = {"query": query}
                            
                            try:
                                # Try to get existing event loop
                                loop = asyncio.get_event_loop()
                                if loop.is_running():
                                    # If we're in an async context, we need to use run_until_complete
                                    # in a new thread to avoid "RuntimeError: cannot be called from a running event loop"
                                    import concurrent.futures
                                    with concurrent.futures.ThreadPoolExecutor() as executor:
                                        future = executor.submit(
                                            asyncio.new_event_loop().run_until_complete,
                                            mcp_client.call_tool(tool_name_ref, arguments, server_type_ref)
                                        )
                                        return future.result()
                                else:
                                    # No running loop, safe to use run_until_complete
                                    return loop.run_until_complete(
                                        mcp_client.call_tool(tool_name_ref, arguments, server_type_ref)
                                    )
                            except RuntimeError:
                                # Fallback: create new event loop
                                new_loop = asyncio.new_event_loop()
                                try:
                                    return new_loop.run_until_complete(
                                        mcp_client.call_tool(tool_name_ref, arguments, server_type_ref)
                                    )
                                finally:
                                    new_loop.close()
                        return mcp_tool_func
                    
                    tools.append(Tool(
                        name=tool_name,
                        func=make_mcp_tool_func(tool_name, server_type),
                        description=tool_info.get("description", f"MCP tool: {tool_name}")
                    ))
            
            # Create metadata
            metadata = PluginMetadata(
                name=plugin_name,
                version="1.0.0",
                description=f"MCP {server_name} plugin",
                category=category,
                author="AgenticAI System",
                dependencies=[],
                config_schema={},
                api_requirements=[]
            )
            
            # Register MCP plugin
            self.plugins[plugin_name] = PluginInfo(
                metadata=metadata,
                status=PluginStatus.ACTIVE,
                tools=tools,
                instance=None,  # MCP servers don't have direct instances
                load_time=datetime.now()
            )
            
            self.logger.info(f"Successfully loaded MCP plugin: {plugin_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading MCP plugin {plugin_name}: {str(e)}")
            raise
    
    async def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a specific plugin"""
        if plugin_name not in self.plugins:
            return False
        
        try:
            plugin_info = self.plugins[plugin_name]
            
            # Cleanup plugin instance if it exists
            if plugin_info.instance and hasattr(plugin_info.instance, 'cleanup'):
                await plugin_info.instance.cleanup()
            
            # Remove from registry
            del self.plugins[plugin_name]
            
            self.logger.info(f"Successfully unloaded plugin: {plugin_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error unloading plugin {plugin_name}: {str(e)}")
            return False
    
    async def reload_plugin(self, plugin_name: str) -> bool:
        """Reload a specific plugin"""
        await self.unload_plugin(plugin_name)
        return await self.load_plugin(plugin_name)
    
    def get_plugin_info(self, plugin_name: str) -> Optional[PluginInfo]:
        """Get information about a specific plugin"""
        return self.plugins.get(plugin_name)
    
    def get_all_plugins(self) -> Dict[str, PluginInfo]:
        """Get information about all loaded plugins"""
        return self.plugins.copy()
    
    def get_plugins_by_category(self, category: PluginCategory) -> Dict[str, PluginInfo]:
        """Get plugins by category"""
        return {
            name: info for name, info in self.plugins.items()
            if info.metadata.category == category
        }
    
    def get_available_tools(self, category: Optional[PluginCategory] = None) -> List[Tool]:
        """Get all available tools, optionally filtered by category"""
        tools = []
        
        for plugin_name, plugin_info in self.plugins.items():
            if plugin_info.status == PluginStatus.ACTIVE:
                if category is None or plugin_info.metadata.category == category:
                    tools.extend(plugin_info.tools)
        
        return tools
    
    def get_plugin_stats(self) -> Dict[str, Any]:
        """Get plugin registry statistics"""
        stats = {
            "total_plugins": len(self.plugins),
            "active_plugins": len([p for p in self.plugins.values() if p.status == PluginStatus.ACTIVE]),
            "error_plugins": len([p for p in self.plugins.values() if p.status == PluginStatus.ERROR]),
            "total_tools": sum(len(p.tools) for p in self.plugins.values()),
            "categories": {}
        }
        
        # Count by category
        for plugin_info in self.plugins.values():
            category = plugin_info.metadata.category.value
            if category not in stats["categories"]:
                stats["categories"][category] = 0
            stats["categories"][category] += 1
        
        return stats
    
    def update_plugin_config(self, plugin_name: str, config: Dict[str, Any]):
        """Update plugin configuration"""
        self.plugin_configs[plugin_name] = config
        self._save_plugin_configs()
    
    async def initialize_all_plugins(self):
        """Discover and load all available plugins"""
        self.logger.info("Initializing all plugins")
        
        discovered_plugins = await self.discover_plugins()
        
        for plugin_name in discovered_plugins:
            try:
                await self.load_plugin(plugin_name)
            except Exception as e:
                self.logger.error(f"Failed to load plugin {plugin_name}: {str(e)}")
        
        stats = self.get_plugin_stats()
        self.logger.info(f"Plugin initialization completed: {stats}")

# Global plugin registry instance
plugin_registry = PluginRegistry() 