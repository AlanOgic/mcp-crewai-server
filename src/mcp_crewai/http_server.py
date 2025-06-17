"""
HTTP Server for MCP CrewAI Server - Monitoring & REST API
Provides HTTP endpoints for monitoring and external access
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

from .server import MCPCrewAIServer
from .monitoring import monitoring_manager, update_system
from .config import get_config

logger = logging.getLogger(__name__)

# Request/Response models
class MCPRequest(BaseModel):
    method: str
    params: Dict[str, Any] = {}

class MCPResponse(BaseModel):
    result: Any = None
    error: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    uptime: str
    version: str

class MCPHTTPServer:
    """HTTP wrapper for MCP CrewAI Server"""
    
    def __init__(self, mcp_server: MCPCrewAIServer):
        self.mcp_server = mcp_server
        self.config = get_config()
        self.app = FastAPI(
            title="MCP CrewAI Server API",
            description="HTTP REST API for MCP CrewAI Server with real-time monitoring",
            version="1.0.0"
        )
        self.startup_time = datetime.now()
        
        # Configure CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure properly for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Setup routes
        self._setup_routes()
        
        logger.info("🌐 HTTP Server initialized for MCP CrewAI")
    
    def _setup_routes(self):
        """Setup all HTTP routes"""
        
        @self.app.get("/health", response_model=HealthResponse)
        async def health_check():
            """Health check endpoint"""
            uptime = str(datetime.now() - self.startup_time).split('.')[0]
            
            # Update system monitoring status
            update_system(
                server_status="healthy",
                memory_usage="0MB",  # TODO: Get actual memory usage
                connections=1
            )
            
            return HealthResponse(
                status="healthy",
                timestamp=datetime.now().isoformat(),
                uptime=uptime,
                version="1.0.0"
            )
        
        @self.app.post("/api/mcp", response_model=MCPResponse)
        async def mcp_endpoint(request: MCPRequest):
            """Main MCP endpoint for tool calls"""
            try:
                # Call the MCP server tool handler directly
                result = await self._handle_tool_call(request.method, request.params)
                
                # Convert TextContent to dict for JSON response
                if result and hasattr(result[0], 'text'):
                    result_data = json.loads(result[0].text)
                else:
                    result_data = {"error": "No result returned"}
                
                return MCPResponse(result=result_data)
                
            except Exception as e:
                logger.error(f"MCP endpoint error: {e}")
                return MCPResponse(error=str(e))
        
        @self.app.get("/api/monitoring/dashboard")
        async def get_dashboard():
            """Get monitoring dashboard data"""
            try:
                dashboard_data = monitoring_manager.get_dashboard_data()
                return JSONResponse(content=dashboard_data)
            except Exception as e:
                logger.error(f"Dashboard endpoint error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/monitoring/events")
        async def get_events(count: int = 50, event_type: Optional[str] = None):
            """Get recent monitoring events"""
            try:
                events = monitoring_manager.get_recent_events(count, event_type)
                return JSONResponse(content={
                    "events": [event.__dict__ for event in events],
                    "count": len(events)
                })
            except Exception as e:
                logger.error(f"Events endpoint error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/monitoring/agent/{agent_id}")
        async def get_agent_details(agent_id: str):
            """Get detailed agent information"""
            try:
                agent_details = monitoring_manager.get_agent_details(agent_id)
                if not agent_details:
                    raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
                return JSONResponse(content=agent_details)
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Agent details endpoint error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/monitoring/evolution")
        async def get_evolution_summary():
            """Get evolution activity summary"""
            try:
                evolution_data = monitoring_manager.get_evolution_summary()
                return JSONResponse(content=evolution_data)
            except Exception as e:
                logger.error(f"Evolution endpoint error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/metrics")
        async def get_metrics():
            """Prometheus-style metrics endpoint"""
            try:
                # Basic metrics - could be extended for Prometheus format
                metrics = monitoring_manager.metrics
                system_status = monitoring_manager.system_status
                
                metrics_data = {
                    **metrics,
                    "active_agents": system_status.active_agents if system_status else 0,
                    "active_crews": system_status.active_crews if system_status else 0,
                    "uptime_seconds": (datetime.now() - self.startup_time).total_seconds()
                }
                
                return JSONResponse(content=metrics_data)
            except Exception as e:
                logger.error(f"Metrics endpoint error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/")
        async def root():
            """Root endpoint with API info"""
            return {
                "name": "MCP CrewAI Server HTTP API",
                "version": "1.0.0",
                "status": "running",
                "endpoints": {
                    "health": "/health",
                    "mcp": "/api/mcp",
                    "dashboard": "/api/monitoring/dashboard",
                    "events": "/api/monitoring/events",
                    "agent_details": "/api/monitoring/agent/{agent_id}",
                    "evolution": "/api/monitoring/evolution",
                    "metrics": "/metrics"
                }
            }
    
    async def _handle_tool_call(self, method: str, params: Dict[str, Any]):
        """Proxy method calls to MCP server"""
        # Call the main tool handler directly
        return await self.mcp_server._handle_call_tool(method, params)
    
    async def run(self, host: str = "0.0.0.0", port: int = 8765):
        """Run the HTTP server"""
        logger.info(f"🚀 Starting HTTP Server on {host}:{port}")
        
        config = uvicorn.Config(
            app=self.app,
            host=host,
            port=port,
            log_level="info",
            access_log=True
        )
        server = uvicorn.Server(config)
        
        # Update monitoring system status
        update_system(
            server_status="starting",
            connections=0
        )
        
        try:
            await server.serve()
        except Exception as e:
            logger.error(f"HTTP Server error: {e}")
            update_system(server_status="error")
            raise


# Factory function to create HTTP server
def create_http_server(mcp_server: MCPCrewAIServer) -> MCPHTTPServer:
    """Create HTTP server instance"""
    return MCPHTTPServer(mcp_server)


# Standalone function to run both servers
async def run_dual_server():
    """Run both MCP stdio server and HTTP server concurrently"""
    from .server import MCPCrewAIServer
    
    # Create MCP server instance
    mcp_server = MCPCrewAIServer()
    
    # Create HTTP server
    http_server = create_http_server(mcp_server)
    
    # Start background evolution for MCP server
    await mcp_server.start_background_evolution()
    
    config = get_config()
    
    # Run HTTP server and MCP stdio server concurrently
    tasks = [
        asyncio.create_task(http_server.run(
            host=config.mcp_server_host,
            port=config.mcp_server_port
        )),
        asyncio.create_task(mcp_server.run())
    ]
    
    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        logger.info("🛑 Servers shutting down...")
        for task in tasks:
            task.cancel()
    except Exception as e:
        logger.error(f"Dual server error: {e}")
        raise


if __name__ == "__main__":
    # Run dual server mode
    asyncio.run(run_dual_server())