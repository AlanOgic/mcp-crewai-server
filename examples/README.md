```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║    ██████╗██████╗ ███████╗██╗    ██╗     █████╗ ██╗    ███████╗██╗   ██╗     ║
║   ██╔════╝██╔══██╗██╔════╝██║    ██║    ██╔══██╗██║    ██╔════╝██║   ██║     ║
║   ██║     ██████╔╝█████╗  ██║ █╗ ██║    ███████║██║    █████╗  ██║   ██║     ║
║   ██║     ██╔══██╗██╔══╝  ██║███╗██║    ██╔══██║██║    ██╔══╝  ╚██╗ ██╔╝     ║
║   ╚██████╗██║  ██║███████╗╚███╔███╔╝    ██║  ██║██║    ███████╗ ╚████╔╝      ║ 
║    ╚═════╝╚═╝  ╚═╝╚══════╝ ╚══╝╚══╝     ╚═╝  ╚═╝╚═╝    ╚══════╝  ╚═══╝       ║
║                                                                              ║
║   ┌─────────────────────────────────────────────────────────────────────┐    ║
║   │  ⚡ AUTONOMOUS EVOLUTION ENGINE  │  🧠 SELF-REFLECTING AGENTS        │    ║
║   │  🔄 DYNAMIC INSTRUCTIONS        │  🔌 UNIVERSAL MCP INTEGRATION     │    ║
║   └─────────────────────────────────────────────────────────────────────┘    ║
║                                                                              ║
║                    🚀 WHERE AI TEAMS EVOLVE AUTONOMOUSLY 🚀                  ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

# 🎯 MCP CrewAI Server - Examples & Demos



This directory contains comprehensive examples demonstrating the revolutionary capabilities of the MCP CrewAI Server.

## 📁 Files Overview

### 🚀 `demo_usage.py`
**Complete demo script showcasing all major features:**
- Creating evolving crews with different personality presets
- Sending dynamic instructions during execution
- Agent MCP client integration with external servers
- Agent self-reflection and autonomous evolution
- Crew self-assessment and autonomous decision making
- Real-world scenario walkthrough

**Run the demo:**
```bash
python examples/demo_usage.py
```

### 🧬 `personality_templates.json`
**Comprehensive personality system configuration:**
- 7 distinct personality templates (analytical, creative, diplomat, etc.)
- Evolution pathways between personality types
- MCP tool affinities for each personality
- Team composition guidelines
- Trait definitions and strengths

### 🔌 `mcp_discovery_configs.json`
**MCP server discovery configurations for different environments:**
- Development team setups
- Content marketing configurations
- Data science environments
- Customer service toolsets
- Creative production workflows
- Business intelligence setups

## 🎭 Personality Templates

### Available Templates

| Template | Description | Key Traits | Ideal Roles |
|----------|-------------|------------|-------------|
| **Analytical** | Data-driven, methodical | High analytical (0.9), Low risk-taking (0.2) | Data Analyst, Research Specialist |
| **Creative** | Innovative, imaginative | High creative (0.9), High adaptable (0.8) | Creative Director, Content Creator |
| **Diplomat** | Empathetic, collaborative | High collaborative (0.9), High adaptable (0.8) | Project Manager, Team Coordinator |
| **Executor** | Pragmatic, efficient | High decisive (0.9), High analytical (0.7) | Operations Manager, DevOps Engineer |
| **Innovator** | Forward-thinking, experimental | High adaptable (0.9), High risk-taking (0.8) | Innovation Lead, R&D Specialist |
| **Specialist** | Deep expertise, technical | High analytical (0.8), Low adaptable (0.4) | Technical Architect, Domain Expert |
| **Visionary** | Big-picture, inspirational | High creative (0.8), High decisive (0.8) | Chief Strategy Officer, Product Visionary |

### Evolution Pathways

Agents can evolve between personality types based on experience:
- **Analytical → Creative**: Develops innovation capabilities
- **Creative → Analytical**: Gains data-driven rigor  
- **Solo → Collaborative**: Becomes team-oriented
- **Specialist → Generalist**: Broadens capabilities
- **Cautious → Bold**: Increases risk tolerance

## 🔌 MCP Environment Configurations

### Development Environment
Perfect for software development teams:
- **GitHub MCP**: Version control, code review, project management
- **Docker MCP**: Container management, deployment
- **PostgreSQL MCP**: Database operations, analytics
- **Slack MCP**: Team communication, automation

### Content Marketing Environment  
Optimized for marketing and content teams:
- **Notion MCP**: Content planning, knowledge management
- **Google Drive MCP**: Asset management, collaboration
- **Social Media MCP**: Content distribution, engagement
- **Canva MCP**: Visual content creation
- **Analytics MCP**: Performance tracking, insights

### Data Science Environment
Tailored for analytics and ML teams:
- **Jupyter MCP**: Notebook management, analysis
- **Kaggle MCP**: Dataset discovery, competitions
- **AWS MCP**: Cloud infrastructure, ML services
- **Tableau MCP**: Business intelligence, visualization

## 🎪 Usage Examples

### 1. Create Evolving Crew

```python
# Via MCP client (Claude, n8n, etc.)
create_evolving_crew({
    "crew_name": "marketing_dream_team",
    "agents_config": [
        {
            "role": "Content Strategist",
            "goal": "Develop data-driven content strategies",
            "backstory": "Expert in content marketing with analytics focus",
            "personality_preset": "analytical"
        },
        {
            "role": "Creative Director", 
            "goal": "Create engaging visual and written content",
            "backstory": "Innovative designer with storytelling expertise",
            "personality_preset": "creative"
        }
    ],
    "tasks": [
        {
            "description": "Analyze Q1 content performance and develop Q2 strategy",
            "agent_role": "Content Strategist"
        },
        {
            "description": "Create Q2 campaign assets based on strategy",
            "agent_role": "Creative Director"
        }
    ],
    "autonomy_level": 0.8
})
```

### 2. Send Dynamic Instructions

```python
# Send guidance during execution
add_dynamic_instruction({
    "crew_id": "marketing_dream_team",
    "instruction": "Focus on B2B segment - they're converting 3x better",
    "instruction_type": "guidance",
    "priority": 4
})

# Provide additional resources
add_dynamic_instruction({
    "crew_id": "marketing_dream_team", 
    "instruction": "Budget increased by 50% - expand creative scope",
    "instruction_type": "resource",
    "priority": 3
})

# Emergency pivot
add_dynamic_instruction({
    "crew_id": "marketing_dream_team",
    "instruction": "Competitor launched similar campaign - differentiate immediately",
    "instruction_type": "pivot", 
    "priority": 5
})
```

### 3. Connect Agents to MCP Servers

```python
# Auto-discover relevant MCP servers
auto_discover_mcp_servers({
    "agent_id": "agent_creative_001",
    "discovery_config": [
        {
            "name": "canva_mcp",
            "command": ["python", "-m", "canva_mcp"],
            "description": "Design tool integration"
        },
        {
            "name": "unsplash_mcp", 
            "command": ["python", "-m", "unsplash_mcp"],
            "description": "Stock photography access"
        }
    ]
})

# Agent uses discovered tool
agent_use_mcp_tool({
    "agent_id": "agent_creative_001",
    "tool_name": "canva_mcp::create_design",
    "arguments": {
        "template": "social_media_post",
        "brand_colors": ["#1e3a8a", "#f59e0b"],
        "content": "Q2 Campaign Launch"
    }
})
```

### 4. Monitor Agent Evolution

```python
# Get agent's self-reflection
get_agent_reflection({
    "agent_id": "agent_creative_001"
})

# Trigger evolution if needed
trigger_agent_evolution({
    "agent_id": "agent_creative_001", 
    "evolution_type": "collaborative"  # Improve teamwork
})

# Check evolved capabilities
get_agent_mcp_status({
    "agent_id": "agent_creative_001"
})
```

## 🌟 Revolutionary Features Demonstrated

### 🧬 Autonomous Evolution
- **Personality Drift**: Gradual trait improvements based on experience
- **Role Specialization**: Agents focus on dominant strengths
- **Radical Transformation**: Complete personality overhauls when needed
- **Collaborative Adaptation**: Improve teamwork and communication

### 🔄 Dynamic Instructions
- **Real-time Guidance**: Send directions without stopping workflows
- **Resource Provision**: Add capabilities mid-execution
- **Strategy Pivots**: Change direction based on new information
- **Emergency Controls**: Stop or redirect when needed

### 🔌 Universal MCP Integration
- **Personality-Based Tool Selection**: Agents choose tools that fit their traits
- **Auto-Discovery**: Agents find and learn new tools autonomously
- **Tool Learning**: Remember what works and improve over time
- **Cross-Server Orchestration**: Coordinate multiple MCP servers

### 🎯 Autonomous Decision Making
- **Self-Assessment**: Crews analyze their own capabilities
- **Gap Identification**: Recognize missing skills or resources
- **Team Rebalancing**: Add/remove agents based on needs
- **Resource Acquisition**: Request tools and data proactively

## 🚀 Getting Started

1. **Install the server:**
   ```bash
   pip install -e .
   ```

2. **Start the MCP server:**
   ```bash
   mcp-crewai-server
   ```

3. **Configure your MCP client** (Claude, n8n, etc.) to connect

4. **Run the demo:**
   ```bash
   python examples/demo_usage.py
   ```

5. **Experiment with personality templates** using the JSON configurations

6. **Set up MCP discovery** for your specific environment

## 🎭 Creating Custom Personalities

Use the personality template structure to create custom agent types:

```json
{
  "my_custom_template": {
    "description": "Your custom personality description",
    "traits": {
      "analytical": 0.7,
      "creative": 0.8,
      "collaborative": 0.6,
      "decisive": 0.9,
      "adaptable": 0.5,
      "risk_taking": 0.4
    },
    "strengths": ["List", "of", "key", "strengths"],
    "ideal_roles": ["Preferred", "role", "types"],
    "tools_preferences": ["preferred_tool_types"]
  }
}
```

## 🔮 Advanced Scenarios

The examples demonstrate increasingly sophisticated scenarios:

1. **Basic Crew Creation** → Simple team setup
2. **Dynamic Instructions** → Real-time control  
3. **MCP Integration** → Universal tool access
4. **Agent Evolution** → Self-improvement cycles
5. **Autonomous Operations** → Fully self-managing teams

## 🌍 Real-World Applications

These examples translate to real business scenarios:

- **Marketing Teams**: Content creation with evolving creative capabilities
- **Development Teams**: Code collaboration with autonomous tool discovery
- **Customer Service**: Support optimization with adaptive agent personalities  
- **Research Teams**: Data analysis with evolving analytical capabilities
- **Creative Agencies**: Design workflows with autonomous resource acquisition

---

**🚀 Ready to experience the future of AI collaboration? Start with the demos and build your own revolutionary AI teams!**