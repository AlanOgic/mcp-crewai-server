#!/usr/bin/env python3
"""
Dynamic Dashboard API for MCP CrewAI Server
Real-time system monitoring and crew management
"""

import os
import sys
import asyncio
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import json
import psutil

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

app = FastAPI(title="MCP CrewAI Dashboard", version="1.0.0")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager for real-time updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                # Remove broken connections
                self.active_connections.remove(connection)

manager = ConnectionManager()

# Data Models
class SystemStatus(BaseModel):
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    uptime: str

class ModelInfo(BaseModel):
    name: str
    provider: str
    status: str
    size: Optional[str] = None
    input_price: float
    output_price: float
    description: str

class ProviderStatus(BaseModel):
    name: str
    display_name: str
    available: bool
    model_count: int
    api_key_configured: bool
    status_message: str

class CrewMetrics(BaseModel):
    total_executions: int
    successful_executions: int
    failed_executions: int
    average_cost: float
    total_tokens: int
    evolution_count: int

# Dynamic system data collection functions
def get_system_status() -> SystemStatus:
    """Get real-time system metrics"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = str(datetime.now() - boot_time).split('.')[0]
        
        return SystemStatus(
            timestamp=datetime.now(),
            cpu_usage=cpu_percent,
            memory_usage=memory.percent,
            disk_usage=disk.percent,
            uptime=uptime
        )
    except Exception as e:
        return SystemStatus(
            timestamp=datetime.now(),
            cpu_usage=0.0,
            memory_usage=0.0,
            disk_usage=0.0,
            uptime="Unknown"
        )

def get_ollama_models() -> List[ModelInfo]:
    """Get real Ollama models installed on system"""
    models = []
    try:
        result = subprocess.run(['ollama', 'list'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if parts:
                        model_name = parts[0]
                        size = parts[1] if len(parts) > 1 else "Unknown"
                        models.append(ModelInfo(
                            name=model_name,
                            provider="ollama",
                            status="available",
                            size=size,
                            input_price=0.0,
                            output_price=0.0,
                            description="Free (Local)"
                        ))
    except Exception as e:
        print(f"Error getting Ollama models: {e}")
    
    return models

def get_cloud_providers() -> List[ProviderStatus]:
    """Get status of cloud LLM providers"""
    providers = []
    
    # Anthropic
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    providers.append(ProviderStatus(
        name="anthropic",
        display_name="Anthropic (Claude)",
        available=bool(anthropic_key),
        model_count=5,  # claude-3-5-sonnet, haiku, opus, etc.
        api_key_configured=bool(anthropic_key),
        status_message="Ready" if anthropic_key else "API key required"
    ))
    
    # OpenAI
    openai_key = os.getenv('OPENAI_API_KEY')
    providers.append(ProviderStatus(
        name="openai",
        display_name="OpenAI (GPT)",
        available=bool(openai_key),
        model_count=6,  # gpt-4o, gpt-4o-mini, o1-pro, etc.
        api_key_configured=bool(openai_key),
        status_message="Ready" if openai_key else "API key required"
    ))
    
    # Google
    google_key = os.getenv('GOOGLE_API_KEY')
    providers.append(ProviderStatus(
        name="google",
        display_name="Google (Gemini)",
        available=bool(google_key),
        model_count=4,  # gemini-2.0-flash, 1.5-pro, etc.
        api_key_configured=bool(google_key),
        status_message="Ready" if google_key else "API key required"
    ))
    
    # Groq
    groq_key = os.getenv('GROQ_API_KEY')
    providers.append(ProviderStatus(
        name="groq",
        display_name="Groq (Fast inference)",
        available=bool(groq_key),
        model_count=5,  # llama-3.1-70b, 8b, mixtral, etc.
        api_key_configured=bool(groq_key),
        status_message="Ready" if groq_key else "API key required"
    ))
    
    return providers

def get_ollama_service_status() -> Dict[str, Any]:
    """Check if Ollama service is running"""
    try:
        result = subprocess.run(['ollama', 'ps'], 
                              capture_output=True, text=True, timeout=5)
        running = result.returncode == 0
        
        # Get loaded models
        loaded_models = []
        if running and result.stdout:
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if parts:
                        loaded_models.append(parts[0])
        
        return {
            "running": running,
            "loaded_models": loaded_models,
            "status_message": "Running" if running else "Not running"
        }
    except Exception:
        return {
            "running": False,
            "loaded_models": [],
            "status_message": "Service check failed"
        }

def get_crew_metrics() -> CrewMetrics:
    """Get crew execution metrics (placeholder - would connect to actual database)"""
    # This would read from your evolution_history.db or similar
    return CrewMetrics(
        total_executions=0,
        successful_executions=0,
        failed_executions=0,
        average_cost=0.0,
        total_tokens=0,
        evolution_count=0
    )

# API Endpoints
@app.get("/api/system/status")
async def system_status():
    """Get current system status"""
    return get_system_status()

@app.get("/api/models/ollama")
async def ollama_models():
    """Get all Ollama models"""
    return get_ollama_models()

@app.get("/api/providers")
async def providers_status():
    """Get status of all LLM providers"""
    return get_cloud_providers()

@app.get("/api/ollama/service")
async def ollama_service():
    """Get Ollama service status"""
    return get_ollama_service_status()

@app.get("/api/metrics/crew")
async def crew_metrics():
    """Get crew execution metrics"""
    return get_crew_metrics()

@app.get("/api/dashboard/overview")
async def dashboard_overview():
    """Get complete dashboard data"""
    ollama_models = get_ollama_models()
    providers = get_cloud_providers()
    ollama_status = get_ollama_service_status()
    system = get_system_status()
    metrics = get_crew_metrics()
    
    return {
        "system": system,
        "ollama": {
            "service": ollama_status,
            "models": ollama_models,
            "model_count": len(ollama_models)
        },
        "providers": providers,
        "metrics": metrics,
        "summary": {
            "total_models": len(ollama_models) + sum(p.model_count for p in providers if p.available),
            "active_providers": len([p for p in providers if p.available]) + (1 if ollama_status["running"] else 0),
            "local_models": len(ollama_models),
            "cloud_providers_configured": len([p for p in providers if p.api_key_configured])
        }
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Send periodic updates
            await asyncio.sleep(5)  # Update every 5 seconds
            overview = await dashboard_overview()
            await websocket.send_text(json.dumps({
                "type": "dashboard_update",
                "data": overview
            }))
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)