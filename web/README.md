# 🚀 MCP CrewAI Web Interface

Interactive web dashboard for managing and monitoring your MCP CrewAI server tools.

## Features

### 🎯 Core Functionality
- **Real-time Dashboard** - Live stats and crew monitoring
- **Crew Management** - Create, run, and monitor autonomous crews
- **Agent Evolution** - Trigger and track agent evolution cycles
- **Dynamic Instructions** - Send real-time instructions to running crews
- **Health Monitoring** - Server health checks and diagnostics
- **WebSocket Updates** - Real-time notifications and updates

### 🛠️ Available Tools Interface
- **Create Evolving Crew** - Interactive form to create new crews
- **Health Check** - Comprehensive server diagnostics
- **Server Configuration** - View current server settings
- **Dynamic Instructions** - Send instructions to active crews
- **Crew Status** - Detailed crew and agent performance metrics
- **Evolution Triggers** - Manual evolution control

## Quick Start

### 1. Launch the Interface
```bash
cd web/
./start_web_interface.sh
```

### 2. Access Dashboard
Open your browser and navigate to:
```
http://localhost:8080
```

### 3. Start Creating Crews
1. Fill in the "Create Evolving Crew" form
2. Set autonomy level (low/medium/high/revolutionary)
3. Add description and click "Create Crew"
4. Monitor your crew in the dashboard

## Interface Components

### 📊 Dashboard Stats
- **Active Crews** - Number of currently running crews
- **Total Agents** - Sum of all agents across crews
- **Evolution Cycles** - Total evolution cycles completed

### 👥 Crew Management
- **Status Monitoring** - Real-time crew status and metrics
- **Evolution Control** - Trigger agent evolution cycles
- **Execution Control** - Start/stop crew execution
- **Performance Metrics** - Success rates and collaboration scores

### 🔧 Tool Interactions
- **Health Checks** - Server diagnostics and status
- **Configuration** - View server settings and features
- **Dynamic Instructions** - Real-time crew communication
- **Real-time Updates** - WebSocket-powered live updates

## API Endpoints

The web interface provides a REST API wrapper around MCP tools:

### Crews
- `GET /api/crews` - List all crews
- `POST /api/crews` - Create new crew
- `GET /api/crews/{id}/status` - Get crew status
- `POST /api/crews/{id}/run` - Run crew
- `POST /api/crews/{id}/evolve` - Trigger evolution

### Instructions
- `POST /api/instructions` - Add dynamic instruction
- `GET /api/instructions/{crew_id}` - List crew instructions

### Server
- `GET /health` - Health check
- `GET /api/server-config` - Server configuration
- `GET /api/monitoring/dashboard` - Monitoring data
- `GET /api/evolution/summary` - Evolution summary

### WebSocket
- `WS /ws` - Real-time updates and notifications

## Architecture

```
Web Browser (Vue.js) 
    ↓ HTTP/WebSocket
FastAPI Server (api_bridge.py)
    ↓ Direct calls
MCP CrewAI Server (server.py)
    ↓ Tool execution
CrewAI + Evolution Engine
```

## Customization

### Adding New Tools
1. Add tool interface in `index.html`
2. Add API endpoint in `api_bridge.py`
3. Connect to MCP tool via `call_mcp_tool()`

### Styling
- Modify CSS in `index.html`
- Uses modern glassmorphism design
- Responsive grid layout
- Dark/light theme ready

## Troubleshooting

### Connection Issues
- Ensure MCP server is running on port 8765
- Check firewall settings for port 8080
- Verify environment variables are set

### Tool Errors
- Check MCP server logs for errors
- Verify API keys are configured
- Ensure all dependencies are installed

### WebSocket Disconnections
- Interface automatically reconnects
- Check network connectivity
- Verify WebSocket support in browser

## Dependencies

- **FastAPI** - Web framework and API server
- **Vue.js 3** - Frontend framework
- **WebSocket** - Real-time communication
- **Chart.js** - Data visualization
- **Axios** - HTTP client
- **Font Awesome** - Icons

## Security

- CORS enabled for development
- API key validation (when configured)
- Input sanitization
- WebSocket authentication ready

## Development

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment
export PYTHONPATH="${PYTHONPATH}:../src"

# Run development server
uvicorn api_bridge:app --reload --host 0.0.0.0 --port 8080
```

### Production Deployment
- Use proper CORS origins
- Enable HTTPS
- Configure reverse proxy
- Set production environment variables

---

🎉 **Your MCP CrewAI tools are now interactive!** Start creating autonomous crews and watch them evolve in real-time.