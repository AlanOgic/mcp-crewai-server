# 🚀 MCP CrewAI Server - Complete Setup Guide

## 📋 Overview

The **MCP CrewAI Server** is a revolutionary advancement over standalone CrewAI, featuring:

- 🧬 **Autonomous Agent Evolution** - Agents evolve personalities based on experience
- 🔄 **Dynamic Runtime Instructions** - Real-time guidance without stopping workflows  
- 🧠 **Self-Reflecting Crews** - Teams that assess and restructure themselves
- 🌐 **Universal MCP Client Integration** - Access to any MCP server as tools
- 💾 **Persistent Cross-Session Memory** - Learning that accumulates over time

## 🎯 Quick Start

```bash
# 1. Clone and setup
cd /Users/alanogic/dev/mcp-crewai-server
cp .env.template .env

# 2. Install dependencies
pip install -e .

# 3. Add your API keys to .env
nano .env

# 4. Test the installation
python3 test_basic.py
python3 test_advanced.py

# 5. Run the revolutionary demo
python3 demo_revolutionary_features.py
```

## 🔑 API Keys & Configuration

### Required API Keys

#### 1. **OpenAI API Key** (Recommended)
```bash
# Get from: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-your-openai-api-key-here
```

#### 2. **Anthropic API Key** (Alternative)
```bash
# Get from: https://console.anthropic.com/
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key-here
```

#### 3. **CrewAI API Key** (Optional - for CrewAI Cloud features)
```bash
# Get from: https://app.crewai.com/
CREWAI_API_KEY=your-crewai-api-key-here
```

### Configuration Files

1. **Copy template**: `cp .env.template .env`
2. **Edit configuration**: `nano .env` or use your preferred editor
3. **Verify setup**: Use the built-in health check tool

## 🛠 Installation Methods

### Method 1: Development Setup (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd mcp-crewai-server

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Copy configuration template
cp .env.template .env

# Edit your API keys
nano .env
```

### Method 2: Production Installation

```bash
# Install from PyPI (when published)
pip install mcp-crewai-server

# Create configuration
curl -O https://raw.githubusercontent.com/user/repo/main/.env.template
cp .env.template .env

# Edit configuration
nano .env
```

### Method 3: Docker Setup

```dockerfile
# Dockerfile included in repository
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -e .
COPY .env.template .env

CMD ["python", "-m", "mcp_crewai.server"]
```

## 🔧 Detailed Configuration

### LLM Provider Setup

#### OpenAI Configuration
```bash
DEFAULT_LLM_PROVIDER=openai
DEFAULT_MODEL=gpt-4-turbo-preview
OPENAI_API_KEY=sk-your-key-here
```

#### Anthropic Configuration  
```bash
DEFAULT_LLM_PROVIDER=anthropic
DEFAULT_MODEL=claude-3-sonnet-20240229
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Advanced Features Configuration

#### Evolution Engine
```bash
EVOLUTION_ENABLED=true
EVOLUTION_FREQUENCY_HOURS=24
AUTO_EVOLUTION_THRESHOLD=0.6
```

#### Dynamic Instructions
```bash
DYNAMIC_INSTRUCTIONS_ENABLED=true
MAX_PENDING_INSTRUCTIONS=50
```

#### Persistent Memory
```bash
MEMORY_ENABLED=true
MEMORY_DATABASE_PATH=./data/agent_memory.db
```

#### Background Tasks
```bash
BACKGROUND_TASKS_ENABLED=true
EVOLUTION_CHECK_INTERVAL=3600
```

### External MCP Server Integration

#### Filesystem MCP
```bash
FILESYSTEM_MCP_ENABLED=true
FILESYSTEM_MCP_ROOT_PATH=/path/to/allowed/directory
```

#### Web MCP
```bash
WEB_MCP_ENABLED=true
WEB_MCP_ALLOWED_DOMAINS=example.com,api.example.com
```

#### Database MCP
```bash
DATABASE_MCP_ENABLED=true
DATABASE_MCP_CONNECTION_STRING=postgresql://user:pass@localhost/db
```

### Security Configuration

```bash
AGENT_SANDBOXING=true
MAX_AGENT_EXECUTION_TIME=300
MAX_AGENT_MEMORY_MB=512
VALIDATE_INSTRUCTIONS=true
```

### Monitoring & Analytics

```bash
MONITORING_ENABLED=true
ANALYTICS_ENABLED=false
METRICS_EXPORT_PATH=./data/metrics.json
HEALTH_CHECK_INTERVAL=60
```

## 🧪 Testing Your Setup

### Basic Tests
```bash
# Test core functionality
python3 test_basic.py

# Expected output:
# ✅ Server instance created successfully!
# ✅ Personality template application works!
# ✅ Evolution engine initialized with strategies!
# ✅ Dynamic instructions system works!
# 🎉 ALL BASIC TESTS PASSED!
```

### Advanced Tests
```bash
# Test revolutionary features
python3 test_advanced.py

# Expected output:
# ✅ Crew created: test_marketing_crew
# ✅ Autonomous agent evolution
# ✅ Dynamic instructions during execution
# ✅ Self-reflecting agents
# ✅ Autonomous crew decision making
# ✅ Team self-assessment
# 🎉 ALL ADVANCED TESTS PASSED!
```

### Full Demonstration
```bash
# Run comprehensive demo
python3 demo_revolutionary_features.py

# Expected output:
# 🧬 DEMO 1: AUTONOMOUS AGENT EVOLUTION
# 🔄 DEMO 2: DYNAMIC RUNTIME INSTRUCTIONS  
# 🧠 DEMO 3: AUTONOMOUS CREW DECISION MAKING
# 🌐 DEMO 4: UNIVERSAL MCP CLIENT INTEGRATION
# 💾 DEMO 5: PERSISTENT CROSS-SESSION MEMORY
```

## 🚀 Running the Server

### Development Mode
```bash
# Start server with hot reload
python3 -m mcp_crewai.server

# Or using the entry point
mcp-crewai-server
```

### Production Mode
```bash
# With logging
mcp-crewai-server 2>&1 | tee server.log

# With process manager (systemd example)
sudo systemctl start mcp-crewai-server
```

### Docker Mode
```bash
# Build and run
docker build -t mcp-crewai-server .
docker run -p 8765:8765 -v $(pwd)/.env:/app/.env mcp-crewai-server
```

## 🔍 Health Monitoring

### Built-in Health Check
```bash
# Using MCP tool (when server is running)
# The server includes health_check, get_server_config, and reload_config tools

# Check configuration
python3 -c "
from mcp_crewai.config import get_config
config = get_config()
summary = config.get_summary()
print('🏥 Health Status:', summary)
"
```

### Configuration Validation
```bash
# Check if production ready
python3 -c "
from mcp_crewai.config import get_config
config = get_config()
is_ready, issues = config.is_production_ready()
print('✅ Production Ready:', is_ready)
if not is_ready:
    print('⚠️ Issues:', issues)
"
```

## 🛠 Troubleshooting

### Common Issues

#### 1. **ImportError: No module named 'mcp_crewai'**
```bash
# Solution: Install in development mode
pip install -e .

# Or check Python path
python3 -c "import sys; print(sys.path)"
```

#### 2. **Configuration not found**
```bash
# Solution: Ensure .env file exists
ls -la .env
cp .env.template .env
```

#### 3. **API Key errors**
```bash
# Solution: Verify API keys
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('OpenAI Key:', 'SET' if os.getenv('OPENAI_API_KEY') else 'MISSING')
print('Anthropic Key:', 'SET' if os.getenv('ANTHROPIC_API_KEY') else 'MISSING')
"
```

#### 4. **Memory/Database errors**
```bash
# Solution: Ensure data directory exists
mkdir -p ./data
chmod 755 ./data
```

#### 5. **Port conflicts**
```bash
# Solution: Change port in .env
MCP_SERVER_PORT=8766
```

### Debug Mode

```bash
# Enable debug logging
LOG_LEVEL=DEBUG

# Run with verbose output
python3 -m mcp_crewai.server --verbose
```

### Log Analysis

```bash
# Check logs for issues
tail -f server.log | grep ERROR
tail -f server.log | grep WARNING
```

## 📚 Usage Examples

### Creating Your First Evolving Crew

```python
from mcp_crewai.server import MCPCrewAIServer
import asyncio
import json

async def create_marketing_team():
    server = MCPCrewAIServer()
    
    crew_config = {
        "crew_name": "marketing_team",
        "agents_config": [
            {
                "role": "Content Strategist",
                "goal": "Develop data-driven content strategies",
                "backstory": "Expert in content planning with 5+ years experience",
                "personality_preset": "analytical"
            },
            {
                "role": "Creative Director", 
                "goal": "Create engaging visual and written content",
                "backstory": "Award-winning creative with strong storytelling skills",
                "personality_preset": "creative"
            }
        ],
        "tasks": [
            {
                "description": "Analyze target audience and develop Q1 content strategy",
                "expected_output": "Comprehensive content strategy document"
            },
            {
                "description": "Create engaging social media campaign concepts",
                "expected_output": "Campaign concepts with visual mockups"
            }
        ],
        "autonomy_level": 0.8
    }
    
    result = await server._create_evolving_crew(crew_config)
    print("Crew created:", json.loads(result[0].text))

# Run the example
asyncio.run(create_marketing_team())
```

### Adding Dynamic Instructions During Execution

```python
async def dynamic_workflow():
    server = MCPCrewAIServer()
    
    # Start crew execution
    execution_task = asyncio.create_task(
        server._run_autonomous_crew({
            "crew_id": "marketing_team",
            "context": {"budget": 50000, "deadline": "30_days"},
            "allow_evolution": True
        })
    )
    
    # Add instructions during execution
    await server._add_dynamic_instruction({
        "crew_id": "marketing_team",
        "instruction": "Focus on B2B segment - higher ROI detected",
        "instruction_type": "guidance",
        "priority": 4
    })
    
    result = await execution_task
    print("Execution result:", json.loads(result[0].text))

asyncio.run(dynamic_workflow())
```

## 🌟 Next Steps

### Production Deployment

1. **Set up monitoring** with proper logging and health checks
2. **Configure external MCP servers** for enhanced capabilities  
3. **Set up database backup** for persistent agent memory
4. **Implement load balancing** for multiple server instances
5. **Set up CI/CD pipeline** for automated deployments

### Advanced Usage

1. **Custom personality presets** - Create domain-specific agent templates
2. **Custom evolution strategies** - Define how agents adapt to your use case
3. **External tool integration** - Connect to your existing systems via MCP
4. **Multi-crew orchestration** - Coordinate multiple teams autonomously
5. **Performance optimization** - Fine-tune for your specific workloads

### Community & Support

- 📖 **Documentation**: In-code documentation and examples
- 🐛 **Issue Reporting**: GitHub issues for bugs and feature requests  
- 💬 **Discussions**: Community discussions for best practices
- 🤝 **Contributing**: Pull requests welcome for improvements

---

**Congratulations! You now have a revolutionary AI collaboration system that evolves, adapts, and improves autonomously. Welcome to the future of CrewAI! 🚀**