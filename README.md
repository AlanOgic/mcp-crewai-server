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

# Autonomous Evolution for CrewAI

## 🌟 What Makes This Interesting?

**MCP CrewAI Server** transforms CrewAI from a static tool into a **living, evolving AI ecosystem**. This isn't just another MCP server - it's the future of autonomous AI collaboration.

### 🧬 AUTONOMOUS EVOLUTION
- **Agents evolve their personalities** over time based on experience
- **Self-reflection cycles** - agents question their own effectiveness  
- **Radical transformations** - complete personality overhauls when needed
- **Dynamic role changes** - agents can change their entire purpose

### 🔄 DYNAMIC INSTRUCTIONS
- **Send instructions to running crews** without stopping workflows
- **Real-time guidance, constraints, resources, feedback**
- **Emergency stops and strategy pivots** mid-execution
- **Skill boosts** - temporarily enhance agent capabilities

### 🔌 MCP CLIENT AGENTS
- **Each agent is an MCP client** - can use ANY MCP server as tools
- **Auto-discovery** of available MCP servers
- **Intelligent tool selection** based on personality and task
- **Learning from tool usage** - agents remember what works

### 🎯 AUTONOMOUS DECISION MAKING
- **Crews self-assess their capabilities** and request what they need
- **Autonomous team rebalancing** - add/remove agents dynamically
- **Radical decisions** - crews can completely change approach
- **Resource acquisition** - request missing tools/data autonomously

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd mcp-crewai-server

# Install dependencies
pip install -e .
```

### Basic Usage

```bash
# Start the MCP server
mcp-crewai-server
```

### Connect to Claude/n8n

Add to your MCP client configuration:

```json
{
  "mcp-crewai-server": {
    "command": ["python", "-m", "mcp_crewai.server"],
    "description": "Autonomous CrewAI evolution"
  }
}
```

---

## 🛠 Core Tools

### 🏗 Crew Management
- `create_evolving_crew` - Create autonomous evolving crew
- `run_autonomous_crew` - Execute with autonomous decision making
- `get_crew_status` - Real-time evolution metrics
- `crew_self_assessment` - Make crew analyze itself

### 🧠 Agent Evolution
- `trigger_agent_evolution` - Force evolution cycle
- `get_agent_reflection` - Get agent's self-analysis
- `create_agent_from_template` - Create from personality templates

### 📡 Dynamic Instructions
- `add_dynamic_instruction` - Send instructions to running crews
- `get_instruction_status` - Check instruction processing
- `list_dynamic_instructions` - View all active instructions

### 🔌 MCP Client Features
- `connect_agent_to_mcp_server` - Connect agent to external MCP servers
- `agent_use_mcp_tool` - Make agent use specific MCP tool
- `get_agent_mcp_status` - View agent's connected tools
- `suggest_tools_for_task` - Get AI suggestions for tools

---

## 💡 Examples

### 1. Evolving Content Creation Team

```python
# Create crew with basic personalities
crew = create_evolving_crew(
    crew_name="content_team",
    agents_config=[
        {
            "role": "Content Strategist",
            "goal": "Create engaging content strategy",
            "backstory": "Expert in content planning",
            "personality_preset": "analytical"
        },
        {
            "role": "Creative Writer", 
            "goal": "Write compelling content",
            "backstory": "Passionate about storytelling",
            "personality_preset": "creative"
        }
    ],
    autonomy_level=0.8  # High autonomy
)

# After 2 weeks, agents have evolved:
# - Strategist became more collaborative (learned teamwork improves results)
# - Writer developed analytical skills (realized data improves creativity)
# - Crew autonomously added SEO specialist (identified missing capability)
```

### 2. Dynamic Instruction During Execution

```python
# Crew is running a complex analysis...
crew_result = run_autonomous_crew("analysis_crew")

# Mid-execution, provide additional guidance
add_dynamic_instruction(
    crew_id="analysis_crew",
    instruction="Focus on Q4 data - that's most critical for decision",
    instruction_type="guidance",
    priority=4
)

# Later, provide new constraints
add_dynamic_instruction(
    crew_id="analysis_crew", 
    instruction="Must complete by 5 PM - executive meeting moved up",
    instruction_type="constraint",
    priority=5
)

# Crew adapts in real-time without stopping!
```

### 3. MCP Tool Integration

```python
# Connect agent to external MCP servers
connect_agent_to_mcp_server(
    agent_id="agent_123",
    server_config={
        "name": "github_mcp",
        "command": ["python", "-m", "github_mcp"],
        "description": "GitHub operations"
    }
)

# Agent automatically discovers and uses tools
suggestions = suggest_tools_for_task(
    agent_id="agent_123",
    task_description="Create a pull request with documentation updates"
)

# Agent intelligently selects and uses GitHub MCP tools
agent_use_mcp_tool(
    agent_id="agent_123",
    tool_name="github_mcp::create_pull_request",
    arguments={"title": "Updated docs", "branch": "feature/docs"}
)
```

---

## 🧬 Evolution Mechanics

### Personality Traits
Each agent has evolving personality traits (0.0 to 1.0):
- **Analytical** - Data-driven approach
- **Creative** - Innovative thinking  
- **Collaborative** - Team-first mindset
- **Decisive** - Quick decision making
- **Adaptable** - Flexibility to change
- **Risk Taking** - Willingness to try new approaches

### Evolution Triggers
- Low performance (< 60% success rate)
- Repeated failures (> 3 failed approaches)
- Age without evolution (> 4 weeks)
- Team imbalance detected
- User feedback patterns

### Evolution Types
- **Personality Drift** - Gradual trait adjustments
- **Role Specialization** - Focus on dominant strengths
- **Collaborative Adaptation** - Improve teamwork
- **Radical Transformation** - Complete personality overhaul

---

## 🎯 Use Cases

### 🏢 Business Automation
- **Evolving customer service teams** that improve from interactions
- **Dynamic marketing crews** that adapt to campaign performance
- **Self-optimizing sales teams** that learn from conversion patterns

### 🔬 Research & Development  
- **Adaptive research teams** that pivot based on findings
- **Multi-disciplinary crews** that develop cross-expertise
- **Hypothesis-driven teams** that evolve methodologies

### 🎨 Creative Projects
- **Evolving creative collectives** that develop unique styles
- **Adaptive content teams** that learn audience preferences
- **Cross-media crews** that master multiple creative domains

### 🛠 Development Teams
- **Self-improving dev crews** that learn from code reviews
- **Adaptive QA teams** that evolve testing strategies  
- **DevOps crews** that optimize based on deployment patterns

---

## 🏗 Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   MCP Client    │    │   MCP Client    │    │   MCP Client    │
│   (Claude/n8n)  │    │   (Other Tool)  │    │   (Custom App)  │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼──────────────┐
                    │     MCP CrewAI Server      │
                    │   (Orchestration Layer)    │
                    └─────────────┬──────────────┘
                                  │
            ┌─────────────────────┼───────────────────────┐
            │                     │                       │
    ┌───────▼────────┐    ┌───────▼────────┐      ┌───────▼────────┐
    │ Evolving Agent │    │ Evolving Agent │      │ Evolving Agent │
    │  (MCP Client)  │    │  (MCP Client)  │      │  (MCP Client)  │
    └────────┬───────┘    └───────┬────────┘      └──────┬─────────┘
             │                    │                      │
             └────────────────────┼──────────────────────┘
                                  │
    ┌─────────────────────────────▼──────────────────────────────┐
    │                External MCP Servers                        │
    │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
    │  │ GitHub MCP  │ │ Notion MCP  │ │ Weather MCP │   ...     │
    │  └─────────────┘ └─────────────┘ └─────────────┘           │
    └────────────────────────────────────────────────────────────┘
```

---

## 🤝 Contributing

This project represents the future of AI collaboration. We welcome contributions that push the boundaries of what's possible:

1. **Novel Evolution Strategies** - New ways agents can evolve
2. **Advanced MCP Integrations** - Connect to more external tools  
3. **Intelligence Improvements** - Better decision-making algorithms
4. **Real-world Applications** - Production use cases and optimizations

---

## 📋 Requirements

- Python 3.9+
- MCP >= 1.0.0
- CrewAI >= 0.70.0
- AsyncIO support

---

## 🔮 Roadmap

### Phase 1 (Current) ✅
- Autonomous agent evolution
- Dynamic instructions
- MCP client integration
- Basic self-reflection

### Phase 2 (Next)
- Multi-crew orchestration
- Advanced learning algorithms  
- Tool creation capabilities
- Performance optimization

### Phase 3 (Future)
- AI teaching AI (meta-learning)
- Crew marketplace
- Cross-server agent migration
- Quantum coherence simulation

---

## 📄 License

MIT License - Build the future of AI collaboration!

---

## 🆘 Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions  
- **Documentation**: Full docs coming soon
- **Community**: Join our Discord

---

**🌟 This isn't just code - it's the evolution of AI collaboration. Welcome to the future! 🌟**
