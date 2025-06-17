# 🚀 MCP CrewAI Server - Quick Start Guide

## What You Have: A Revolutionary AI System

You now have a **game-changing MCP server** that transforms CrewAI from static to autonomous. Here's what to do:

## ⚡ Immediate Setup (5 minutes)

### 1. Install Dependencies
```bash
cd /Users/alanogic/dev/mcp-crewai-server
pip install -e .
```

### 2. Configure API Keys
```bash
# Copy the template
cp .env.template .env

# Edit with your API keys
nano .env
```

**Required**: Add at least one of these API keys to `.env`:
```bash
# For OpenAI (recommended)
OPENAI_API_KEY=sk-your-openai-key-here

# Or for Anthropic
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
```

### 3. Test Everything Works
```bash
# Test basic functionality
python3 test_basic.py

# Test revolutionary features  
python3 test_advanced.py

# Run full demonstration
python3 demo_revolutionary_features.py
```

## 🎯 What You Can Do NOW

### Instant Demo - See the Revolution
```bash
python3 demo_revolutionary_features.py
```

This shows all revolutionary features:
- 🧬 **Agents evolving their personalities** based on experience
- 🔄 **Dynamic instructions** added during execution without stopping
- 🧠 **Autonomous crew decisions** about team composition
- 🌐 **Universal MCP client integration** for any external tools
- 💾 **Persistent memory** that survives restarts

### Start the MCP Server
```bash
# Method 1: Direct execution
python3 -m mcp_crewai.server

# Method 2: Using entry point
mcp-crewai-server
```

### Use in Claude Code or Other MCP Clients

Add to your MCP configuration:
```json
{
  "mcp-crewai-server": {
    "command": ["python", "-m", "mcp_crewai.server"],
    "description": "Revolutionary autonomous CrewAI evolution"
  }
}
```

## 🛠 Available Tools

When connected via MCP, you have access to **21 revolutionary tools**:

### 🏗 Core Evolution Tools
- `create_evolving_crew` - Create teams that evolve autonomously
- `run_autonomous_crew` - Execute with self-modification capabilities
- `trigger_agent_evolution` - Force evolution cycles
- `get_agent_reflection` - See how agents analyze themselves

### 🔄 Dynamic Control Tools
- `add_dynamic_instruction` - Send instructions to running crews
- `list_dynamic_instructions` - View all active instructions
- `get_workflow_status` - Real-time execution monitoring

### 🌐 MCP Integration Tools
- `connect_agent_to_mcp_server` - Connect agents to external tools
- `agent_use_mcp_tool` - Make agents use specific tools
- `suggest_tools_for_task` - AI-powered tool recommendations

### 📊 Monitoring Tools
- `health_check` - Comprehensive system health
- `get_server_config` - Complete configuration status
- `reload_config` - Hot-reload configuration changes

## 💡 Quick Examples

### Create Your First Evolving Team
```python
# Via MCP tool call in Claude Code:
create_evolving_crew({
    "crew_name": "marketing_team",
    "agents_config": [
        {
            "role": "Content Strategist",
            "goal": "Develop data-driven content strategies", 
            "backstory": "Expert in content planning",
            "personality_preset": "analytical"
        },
        {
            "role": "Creative Director",
            "goal": "Create engaging visual content",
            "backstory": "Award-winning creative professional",
            "personality_preset": "creative"
        }
    ],
    "tasks": [
        {
            "description": "Develop Q1 content strategy",
            "expected_output": "Comprehensive strategy document"
        }
    ],
    "autonomy_level": 0.8
})
```

### Add Instructions During Execution
```python
# Start a crew running, then add guidance
add_dynamic_instruction({
    "crew_id": "marketing_team",
    "instruction": "Focus on B2B segment - higher conversion rates detected",
    "instruction_type": "guidance", 
    "priority": 4
})
```

### Force Agent Evolution
```python
# Make an agent evolve based on performance
trigger_agent_evolution({
    "agent_id": "agent_12345",
    "evolution_type": "collaborative"
})
```

## 🔧 Configuration Options

Your `.env` file controls everything:

### Essential Settings
```bash
# LLM Configuration
DEFAULT_LLM_PROVIDER=openai
DEFAULT_MODEL=gpt-4-turbo-preview
OPENAI_API_KEY=your-key-here

# Revolutionary Features
EVOLUTION_ENABLED=true
DYNAMIC_INSTRUCTIONS_ENABLED=true
MEMORY_ENABLED=true
```

### Advanced Settings
```bash
# Evolution Control
EVOLUTION_FREQUENCY_HOURS=24
AUTO_EVOLUTION_THRESHOLD=0.6

# Performance
MAX_AGENT_EXECUTION_TIME=300
MAX_AGENT_MEMORY_MB=512

# External MCP Servers
FILESYSTEM_MCP_ENABLED=true
WEB_MCP_ENABLED=true
DATABASE_MCP_ENABLED=true
```

## 🆘 Troubleshooting

### Common Issues & Quick Fixes

**"ImportError: No module named 'mcp_crewai'"**
```bash
pip install -e .
```

**"Configuration not found"**
```bash
cp .env.template .env
nano .env  # Add your API keys
```

**"API Key not working"**
```bash
# Test your keys
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('OpenAI:', 'SET' if os.getenv('OPENAI_API_KEY') else 'MISSING')
"
```

**"Server won't start"**
```bash
# Check configuration
python3 -c "
from mcp_crewai.config import get_config
config = get_config()
ready, issues = config.is_production_ready()
print('Ready:', ready)
print('Issues:', issues)
"
```

## 🎉 You're Ready!

You now have the **most advanced CrewAI system ever built**:

✅ **Agents that evolve autonomously** over time  
✅ **Real-time instruction capabilities** during execution  
✅ **Self-reflecting and self-modifying teams**  
✅ **Universal tool integration** via MCP  
✅ **Persistent learning** across sessions  

### Next Steps:
1. **Run the demo** to see everything in action
2. **Start the MCP server** and connect it to Claude Code
3. **Create your first evolving crew** for a real use case
4. **Watch them evolve** and improve over time

**Welcome to the future of AI collaboration! 🌟**

---

For detailed documentation: See `SETUP.md`  
For architecture details: See `README.md`  
For support: Create GitHub issues