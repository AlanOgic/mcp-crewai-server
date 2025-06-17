"""
MCP Client Agent - Agents that can use other MCP servers as tools
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
import httpx
from dataclasses import dataclass

from mcp import ClientSession
from mcp.client.stdio import stdio_client

from .models import EvolvingAgent

logger = logging.getLogger(__name__)


@dataclass
class MCPServerConnection:
    """Configuration for MCP server connection"""
    name: str
    command: List[str]
    description: str
    capabilities: List[str] = None
    session: Optional[ClientSession] = None
    connected: bool = False
    last_used: Optional[datetime] = None


class MCPClientAgent(EvolvingAgent):
    """
    🔌 AGENT WITH MCP CLIENT CAPABILITIES
    
    Each agent can connect to and use multiple MCP servers as tools
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # MCP client capabilities - use __dict__ to bypass Pydantic restrictions
        self.__dict__['mcp_servers'] = {}
        self.__dict__['available_tools'] = {}
        self.__dict__['tool_usage_history'] = []
        self.__dict__['preferred_tools'] = set()
        
        # Auto-discovery and connection
        self.__dict__['_discovery_enabled'] = True
        self.__dict__['_auto_connect'] = True
    
    async def connect_to_mcp_server(self, server_config: Dict[str, Any]) -> bool:
        """Connect to an MCP server"""
        server_name = server_config["name"]
        
        try:
            connection = MCPServerConnection(
                name=server_name,
                command=server_config["command"],
                description=server_config.get("description", ""),
                capabilities=server_config.get("capabilities", [])
            )
            
            # Start stdio client connection
            async with stdio_client(connection.command) as (read, write):
                async with ClientSession(read, write) as session:
                    # Initialize connection
                    init_result = await session.initialize()
                    
                    # Store active session
                    connection.session = session
                    connection.connected = True
                    self.mcp_servers[server_name] = connection
                    
                    # Discover available tools
                    await self._discover_tools(server_name, session)
                    
                    logger.info(f"🔌 Agent {self.agent_id} connected to MCP server: {server_name}")
                    
                    # Keep session alive in background
                    asyncio.create_task(self._maintain_connection(server_name, session))
                    
                    return True
                    
        except Exception as e:
            logger.error(f"Failed to connect to MCP server {server_name}: {e}")
            return False
    
    async def _discover_tools(self, server_name: str, session: ClientSession):
        """Discover available tools from MCP server"""
        try:
            # List available tools
            tools_result = await session.list_tools()
            
            for tool in tools_result.tools:
                tool_key = f"{server_name}::{tool.name}"
                self.available_tools[tool_key] = {
                    "server": server_name,
                    "name": tool.name,
                    "description": tool.description,
                    "schema": tool.inputSchema,
                    "capabilities": getattr(tool, 'capabilities', [])
                }
                
                # Auto-add to preferred tools based on agent personality
                if self._should_prefer_tool(tool):
                    self.preferred_tools.add(tool_key)
            
            logger.info(f"🔍 Discovered {len(tools_result.tools)} tools from {server_name}")
            
        except Exception as e:
            logger.error(f"Failed to discover tools from {server_name}: {e}")
    
    def _should_prefer_tool(self, tool) -> bool:
        """Determine if agent should prefer this tool based on personality"""
        tool_desc = tool.description.lower()
        
        # Analytical agents prefer data/analysis tools
        if self.personality_traits["analytical"].value > 0.7:
            if any(word in tool_desc for word in ['analyze', 'data', 'calculate', 'measure']):
                return True
        
        # Creative agents prefer content/creative tools
        if self.personality_traits["creative"].value > 0.7:
            if any(word in tool_desc for word in ['create', 'generate', 'design', 'write']):
                return True
        
        # Collaborative agents prefer communication tools
        if self.personality_traits["collaborative"].value > 0.7:
            if any(word in tool_desc for word in ['send', 'notify', 'share', 'communicate']):
                return True
        
        return False
    
    async def _maintain_connection(self, server_name: str, session: ClientSession):
        """Maintain active connection to MCP server"""
        try:
            while self.mcp_servers[server_name].connected:
                await asyncio.sleep(30)  # Heartbeat every 30 seconds
                
                # Simple ping to keep connection alive
                try:
                    await session.list_tools()
                except Exception as e:
                    logger.warning(f"Connection to {server_name} lost: {e}")
                    self.mcp_servers[server_name].connected = False
                    break
                    
        except Exception as e:
            logger.error(f"Connection maintenance failed for {server_name}: {e}")
            self.mcp_servers[server_name].connected = False
    
    async def use_mcp_tool(self, tool_name: str, arguments: Dict[str, Any], context: str = "") -> Dict[str, Any]:
        """Use an MCP tool from connected servers"""
        
        # Find the tool
        if tool_name not in self.available_tools:
            # Try to find by partial name
            matching_tools = [t for t in self.available_tools.keys() if tool_name in t]
            if not matching_tools:
                return {"error": f"Tool '{tool_name}' not found"}
            tool_name = matching_tools[0]  # Use first match
        
        tool_info = self.available_tools[tool_name]
        server_name = tool_info["server"]
        
        if server_name not in self.mcp_servers or not self.mcp_servers[server_name].connected:
            return {"error": f"Not connected to server {server_name}"}
        
        try:
            session = self.mcp_servers[server_name].session
            
            # Call the tool
            result = await session.call_tool(
                name=tool_info["name"],
                arguments=arguments
            )
            
            # Record usage
            usage_record = {
                "timestamp": datetime.now().isoformat(),
                "tool": tool_name,
                "server": server_name,
                "arguments": arguments,
                "context": context,
                "success": True,
                "result_summary": str(result)[:200]  # First 200 chars
            }
            self.tool_usage_history.append(usage_record)
            
            # Update server last used
            self.mcp_servers[server_name].last_used = datetime.now()
            
            # Learn from successful usage
            self._learn_from_tool_usage(tool_name, True, context)
            
            return {
                "success": True,
                "result": result,
                "tool": tool_name,
                "server": server_name
            }
            
        except Exception as e:
            logger.error(f"Failed to use tool {tool_name}: {e}")
            
            # Record failed usage
            usage_record = {
                "timestamp": datetime.now().isoformat(),
                "tool": tool_name,
                "server": server_name,
                "arguments": arguments,
                "context": context,
                "success": False,
                "error": str(e)
            }
            self.tool_usage_history.append(usage_record)
            
            # Learn from failure
            self._learn_from_tool_usage(tool_name, False, context)
            
            return {"error": str(e), "tool": tool_name}
    
    def _learn_from_tool_usage(self, tool_name: str, success: bool, context: str):
        """Learn from tool usage patterns"""
        if success:
            # Add to preferred tools if successful
            self.preferred_tools.add(tool_name)
            
            # Record successful strategy
            strategy = f"used_{tool_name}_for_{context[:20]}"
            if hasattr(self.memory, 'successful_strategies'):
                self.memory.successful_strategies.append(strategy)
        else:
            # Remove from preferred tools if failed
            self.preferred_tools.discard(tool_name)
            
            # Record failed approach
            approach = f"tried_{tool_name}_for_{context[:20]}"
            if hasattr(self.memory, 'failed_approaches'):
                self.memory.failed_approaches.append(approach)
    
    def suggest_tools_for_task(self, task_description: str) -> List[Dict[str, Any]]:
        """Suggest MCP tools that might help with a task"""
        suggestions = []
        task_lower = task_description.lower()
        
        # Analyze task and match with available tools
        for tool_key, tool_info in self.available_tools.items():
            tool_desc = tool_info["description"].lower()
            
            # Simple keyword matching (could be improved with embeddings)
            relevance_score = 0.0
            
            # Check description overlap
            task_words = set(task_lower.split())
            desc_words = set(tool_desc.split())
            overlap = len(task_words.intersection(desc_words))
            relevance_score += overlap * 0.1
            
            # Boost score for preferred tools
            if tool_key in self.preferred_tools:
                relevance_score += 0.3
            
            # Boost score based on personality fit
            if self._tool_fits_personality(tool_info):
                relevance_score += 0.2
            
            if relevance_score > 0.1:  # Minimum threshold
                suggestions.append({
                    "tool": tool_key,
                    "description": tool_info["description"],
                    "relevance_score": relevance_score,
                    "server": tool_info["server"],
                    "preferred": tool_key in self.preferred_tools
                })
        
        # Sort by relevance score
        suggestions.sort(key=lambda x: x["relevance_score"], reverse=True)
        return suggestions[:5]  # Top 5 suggestions
    
    def _tool_fits_personality(self, tool_info: Dict[str, Any]) -> bool:
        """Check if tool fits agent's personality"""
        tool_desc = tool_info["description"].lower()
        
        # Check personality alignment
        if self.personality_traits["analytical"].value > 0.6:
            if any(word in tool_desc for word in ['analyze', 'calculate', 'data', 'metrics']):
                return True
        
        if self.personality_traits["creative"].value > 0.6:
            if any(word in tool_desc for word in ['create', 'generate', 'design', 'art']):
                return True
        
        if self.personality_traits["collaborative"].value > 0.6:
            if any(word in tool_desc for word in ['team', 'share', 'communicate', 'notify']):
                return True
        
        return False
    
    async def auto_discover_servers(self, discovery_config: List[Dict[str, Any]]):
        """Auto-discover and connect to available MCP servers"""
        if not self._discovery_enabled:
            return
        
        connection_results = []
        
        for server_config in discovery_config:
            try:
                if self._auto_connect:
                    success = await self.connect_to_mcp_server(server_config)
                    connection_results.append({
                        "server": server_config["name"],
                        "connected": success
                    })
            except Exception as e:
                logger.error(f"Auto-discovery failed for {server_config['name']}: {e}")
                connection_results.append({
                    "server": server_config["name"],
                    "connected": False,
                    "error": str(e)
                })
        
        # Update memory with discovery results
        self.memory.experiences.append({
            "event": "mcp_server_discovery",
            "timestamp": datetime.now().isoformat(),
            "results": connection_results
        })
        
        logger.info(f"🔍 Agent {self.agent_id} auto-discovered {len(connection_results)} MCP servers")
    
    def get_mcp_status(self) -> Dict[str, Any]:
        """Get status of MCP connections and tools"""
        return {
            "agent_id": self.agent_id,
            "connected_servers": len([s for s in self.mcp_servers.values() if s.connected]),
            "total_servers": len(self.mcp_servers),
            "available_tools": len(self.available_tools),
            "preferred_tools": len(self.preferred_tools),
            "tool_usage_count": len(self.tool_usage_history),
            "servers": {
                name: {
                    "connected": conn.connected,
                    "description": conn.description,
                    "last_used": conn.last_used.isoformat() if conn.last_used else None
                }
                for name, conn in self.mcp_servers.items()
            },
            "recent_tool_usage": self.tool_usage_history[-5:]  # Last 5 usages
        }
    
    def disconnect_from_server(self, server_name: str) -> bool:
        """Disconnect from an MCP server"""
        if server_name in self.mcp_servers:
            self.mcp_servers[server_name].connected = False
            
            # Remove tools from this server
            tools_to_remove = [
                tool_key for tool_key, tool_info in self.available_tools.items()
                if tool_info["server"] == server_name
            ]
            
            for tool_key in tools_to_remove:
                del self.available_tools[tool_key]
                self.preferred_tools.discard(tool_key)
            
            logger.info(f"🔌 Agent {self.agent_id} disconnected from {server_name}")
            return True
        
        return False