#!/usr/bin/env python3
"""
MCP CrewAI Web Interface API Bridge
Connects the web dashboard to MCP CrewAI server tools
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Import MCP server components
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from mcp_crewai.server import MCPCrewAIServer
from mcp_crewai.config import get_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for API requests
class CrewCreateRequest(BaseModel):
    name: str = Field(..., description="Name of the crew")
    autonomy_level: str = Field(default="medium", description="Autonomy level: low, medium, high, revolutionary")
    description: str = Field(..., description="Description of the crew's purpose")
    goal: str = Field(default="", description="Goal for the agents")
    agents: List[Dict[str, Any]] = Field(default=[], description="Initial agents configuration")

class InstructionRequest(BaseModel):
    crew_id: str = Field(..., description="Target crew ID")
    instruction: str = Field(..., description="Instruction text") 
    priority: str = Field(default="medium", description="Priority level")

class ToolCallRequest(BaseModel):
    tool_name: str = Field(..., description="Name of the MCP tool to call")
    arguments: Dict[str, Any] = Field(default={}, description="Tool arguments")

# Global MCP server instance
mcp_server: Optional[MCPCrewAIServer] = None
websocket_connections: List[WebSocket] = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global mcp_server
    
    # Startup
    logger.info("🚀 Starting MCP CrewAI Web Interface...")
    try:
        mcp_server = MCPCrewAIServer()
        logger.info("✅ MCP Server initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize MCP Server: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down MCP CrewAI Web Interface...")
    if mcp_server:
        # Cleanup if needed
        pass

# Create FastAPI app
app = FastAPI(
    title="MCP CrewAI Web Interface",
    description="Interactive web interface for MCP CrewAI server tools",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
app.mount("/static", StaticFiles(directory=os.path.dirname(__file__)), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    """Serve the main dashboard HTML"""
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    return FileResponse(html_path)

@app.get("/health")
async def health_check():
    """Server health check endpoint"""
    try:
        if not mcp_server:
            raise HTTPException(status_code=503, detail="MCP Server not initialized")
        
        # Call MCP health check tool
        result = await call_mcp_tool("health_check", {})
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "mcp_status": result,
            "uptime": str(datetime.now() - mcp_server.startup_time) if mcp_server else "unknown"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")

@app.get("/api/server-config")
async def get_server_config():
    """Get server configuration"""
    try:
        result = await call_mcp_tool("get_server_config", {})
        return result
    except Exception as e:
        logger.error(f"Failed to get server config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/crews")
async def list_crews():
    """List all active crews"""
    try:
        result = await call_mcp_tool("list_active_crews", {})
        return result
    except Exception as e:
        logger.error(f"Failed to list crews: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/crews")
async def create_crew(request: CrewCreateRequest):
    """Create a new evolving crew"""
    try:
        logger.info(f"Creating crew: {request}")
        logger.info(f"Request data: name={request.name}, autonomy={request.autonomy_level}, goal={request.goal}")
        # Convert autonomy level to float
        autonomy_map = {
            "low": 0.3,
            "medium": 0.5, 
            "high": 0.7,
            "revolutionary": 0.9
        }
        autonomy_float = autonomy_map.get(request.autonomy_level, 0.5)
        
        # Convert agents to expected format
        agents_config = []
        for agent in (request.agents or []):
            agent_config = {
                "role": agent.get("role", "Team Member"),
                "goal": request.goal or f"Achieve objectives for {request.name}",
                "backstory": f"An experienced {agent.get('role', 'team member')} working on {request.name}",
                "personality_preset": agent.get("personality", "analytical")
            }
            agents_config.append(agent_config)
        
        # Default agent if none provided
        if not agents_config:
            agents_config = [
                {
                    "role": "Team Leader",
                    "goal": request.goal or f"Lead and coordinate the {request.name} effectively",
                    "backstory": f"Leading the {request.name} with strategic thinking",
                    "personality_preset": "analytical"
                }
            ]

        # Convert request to MCP tool arguments
        args = {
            "crew_name": request.name,
            "autonomy_level": autonomy_float,
            "description": request.description,
            "agents_config": agents_config,
            "tasks": [
                {
                    "description": f"Execute {request.description}",
                    "expected_output": "Comprehensive task completion report"
                }
            ]
        }
        
        result = await call_mcp_tool("create_evolving_crew", args)
        
        # Broadcast update to websocket clients
        await broadcast_update("crew_created", result)
        
        return result
    except Exception as e:
        logger.error(f"Failed to create crew: {e}")
        logger.error(f"Exception type: {type(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/crews/{crew_id}/status")
async def get_crew_status(crew_id: str):
    """Get detailed crew status"""
    try:
        result = await call_mcp_tool("get_crew_status", {"crew_id": crew_id})
        return result
    except Exception as e:
        logger.error(f"Failed to get crew status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/crews/{crew_id}/run")
async def run_crew(crew_id: str):
    """Run autonomous crew"""
    try:
        result = await call_mcp_tool("run_autonomous_crew", {"crew_id": crew_id})
        
        # Broadcast update to websocket clients
        await broadcast_update("crew_execution_started", {"crew_id": crew_id, "result": result})
        
        return result
    except Exception as e:
        logger.error(f"Failed to run crew: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/crews/{crew_id}/evolve")
async def trigger_evolution(crew_id: str):
    """Trigger agent evolution for crew"""
    try:
        # Get crew agents first
        crew_status = await call_mcp_tool("get_crew_status", {"crew_id": crew_id})
        
        results = []
        for agent in crew_status.get("agents", []):
            agent_id = agent.get("agent_id")
            if agent_id:
                result = await call_mcp_tool("trigger_agent_evolution", {
                    "agent_id": agent_id,
                    "evolution_type": "personality"
                })
                results.append(result)
        
        # Broadcast update to websocket clients
        await broadcast_update("evolution_triggered", {"crew_id": crew_id, "results": results})
        
        return {"crew_id": crew_id, "evolution_results": results}
    except Exception as e:
        logger.error(f"Failed to trigger evolution: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/instructions")
async def add_dynamic_instruction(request: InstructionRequest):
    """Add dynamic instruction to running crew"""
    try:
        args = {
            "crew_id": request.crew_id,
            "instruction": request.instruction,
            "priority": request.priority
        }
        
        result = await call_mcp_tool("add_dynamic_instruction", args)
        
        # Broadcast update to websocket clients
        await broadcast_update("instruction_added", result)
        
        return result
    except Exception as e:
        logger.error(f"Failed to add instruction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/instructions/{crew_id}")
async def list_instructions(crew_id: str):
    """List dynamic instructions for crew"""
    try:
        result = await call_mcp_tool("list_dynamic_instructions", {"crew_id": crew_id})
        return result
    except Exception as e:
        logger.error(f"Failed to list instructions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tools/call")
async def call_tool(request: ToolCallRequest):
    """Generic tool call endpoint"""
    try:
        result = await call_mcp_tool(request.tool_name, request.arguments)
        return result
    except Exception as e:
        logger.error(f"Failed to call tool {request.tool_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/monitoring/dashboard")
async def get_monitoring_dashboard():
    """Get monitoring dashboard data"""
    try:
        result = await call_mcp_tool("get_monitoring_dashboard", {})
        return result
    except Exception as e:
        logger.error(f"Failed to get monitoring dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/evolution/summary")
async def get_evolution_summary():
    """Get evolution activity summary"""
    try:
        result = await call_mcp_tool("get_evolution_summary", {})
        return result
    except Exception as e:
        logger.error(f"Failed to get evolution summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/monitoring/live-events")
async def get_live_events():
    """Get recent live monitoring events"""
    try:
        result = await call_mcp_tool("get_live_events", {})
        return result
    except Exception as e:
        # Return mock events for demo purposes
        logger.warning(f"Live events not available: {e}")
        return {
            "events": [
                {
                    "type": "thinking",
                    "agent_name": "Research Lead",
                    "message": "Analyzing market trends",
                    "details": "Processing latest data from multiple sources",
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }

@app.post("/api/mcp")
async def mcp_endpoint(request: dict):
    """MCP tool endpoint for monitor compatibility"""
    try:
        method = request.get("method")
        params = request.get("params", {})
        
        result = await call_mcp_tool(method, params)
        return {"result": result, "error": None}
    except Exception as e:
        logger.error(f"MCP endpoint error: {e}")
        return {"result": None, "error": str(e)}

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    websocket_connections.append(websocket)
    
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_connections.remove(websocket)

async def broadcast_update(event_type: str, data: Any):
    """Broadcast update to all connected websocket clients"""
    if not websocket_connections:
        return
    
    message = {
        "type": event_type,
        "timestamp": datetime.now().isoformat(),
        "data": data
    }
    
    # Send to all connected clients
    disconnected = []
    for websocket in websocket_connections:
        try:
            await websocket.send_text(json.dumps(message))
        except:
            disconnected.append(websocket)
    
    # Remove disconnected clients
    for ws in disconnected:
        websocket_connections.remove(ws)

async def call_mcp_tool(tool_name: str, arguments: Dict[str, Any]) -> Any:
    """Helper function to call MCP tools"""
    if not mcp_server:
        raise Exception("MCP Server not initialized")
    
    try:
        # Call the MCP server tool
        result = await mcp_server._handle_call_tool(tool_name, arguments)
        
        # Extract text content from MCP response
        if isinstance(result, list) and result:
            if hasattr(result[0], 'text'):
                # Try to parse as JSON if possible
                try:
                    return json.loads(result[0].text)
                except (json.JSONDecodeError, AttributeError):
                    return result[0].text
            return result[0]
        
        return result
        
    except Exception as e:
        logger.error(f"MCP tool call failed: {tool_name} - {e}")
        raise

if __name__ == "__main__":
    config = get_config()
    
    # Run the web server
    uvicorn.run(
        "api_bridge:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )