# MCP CrewAI Server - Project Structure

## 🚀 Main Files

- **`main.py`** - Main entry point, choose execution mode
- **`crew_builder.py`** - Agent 1 researches and builds optimal crews
- **`start_http.py`** - Start HTTP server interface

## 📁 Core Directories

### `/src/mcp_crewai/`
Core MCP server implementation:
- `server.py` - Main MCP server with all tools
- `models.py` - Agent and crew models with evolution
- `task_termination.py` - Task termination system (replaces timeouts)
- `config.py` - Configuration with verbose settings
- `evolution.py` - Agent evolution engine
- `dynamic_instructions.py` - Real-time instruction injection
- `monitoring.py` - Real-time monitoring system
- `web_search.py` - Web search capabilities

### `/examples/`
Example scripts and demonstrations:
- `verbose_crew_execution.py` - Maximum verbosity crew demo
- `simple_crew_interface.py` - Simple interface
- `goal_to_crew.py` - Goal-based crew creation
- `show_intelligent_crew_working.py` - Intelligence demo

### `/tests/`
Test scripts:
- `test_basic.py` - Basic functionality tests
- `test_evolution.py` - Evolution system tests
- `test_real_crewai_execution.py` - Real execution tests
- `test_verbose_execution_with_termination.py` - Termination tests

### `/tools/`
Utility tools:
- `real_crewai_execution.py` - Real CrewAI execution utility
- `need_driven_workflow.py` - Need-driven workflow tool

### `/archive/`
Archived files and old versions

### `/exported_results/`
All execution results and generated content

## 🔧 Key Features Implemented

1. **Agent 1 Builds Crews**: Agent 1 researches goals and designs optimal crews
2. **Maximum Verbosity**: See every agent conversation and decision
3. **Task Termination**: Press 'G' to terminate agents gracefully (no timeouts)
4. **Web Search**: Agents have real internet access via Brave Search API
5. **Results Organization**: All outputs saved to exported_results/

## 🚀 Quick Start

```bash
# Run crew builder (Agent 1 designs crew)
python3 main.py crew "Create FAQ for Cyanview CI0"

# Or directly:
python3 crew_builder.py "Your goal here"

# Start MCP server
python3 main.py server

# Run examples
python3 main.py examples
```

## 📋 Configuration

- **`.env`** - Environment variables and API keys
- **`pyproject.toml`** - Python dependencies
- **`docker-compose.yml`** - Docker deployment

## 🔥 Revolutionary Features

- **No Fake Demos**: Only real execution with real agents
- **Agent 1 Control**: Agent 1 determines all crew settings
- **Internet Research**: Agents research actual information
- **Task Termination**: Graceful termination with partial results
- **Maximum Transparency**: See everything the crew does