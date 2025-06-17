"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║    ██████╗██████╗ ███████╗██╗    ██╗     █████╗ ██╗    ███████╗██╗   ██╗    ║
║   ██╔════╝██╔══██╗██╔════╝██║    ██║    ██╔══██╗██║    ██╔════╝██║   ██║    ║
║   ██║     ██████╔╝█████╗  ██║ █╗ ██║    ███████║██║    █████╗  ██║   ██║    ║
║   ██║     ██╔══██╗██╔══╝  ██║███╗██║    ██╔══██║██║    ██╔══╝  ╚██╗ ██╔╝    ║
║   ╚██████╗██║  ██║███████╗╚███╔███╔╝    ██║  ██║██║    ███████╗ ╚████╔╝     ║
║    ╚═════╝╚═╝  ╚═╝╚══════╝ ╚══╝╚══╝     ╚═╝  ╚═╝╚═╝    ╚══════╝  ╚═══╝      ║
║                                                                              ║
║   ┌─────────────────────────────────────────────────────────────────────┐   ║
║   │  ⚡ AUTONOMOUS EVOLUTION ENGINE  │  🧠 SELF-REFLECTING AGENTS    │   ║
║   │  🔄 DYNAMIC INSTRUCTIONS        │  🔌 UNIVERSAL MCP INTEGRATION  │   ║
║   └─────────────────────────────────────────────────────────────────────┘   ║
║                                                                              ║
║                    🚀 WHERE AI TEAMS EVOLVE AUTONOMOUSLY 🚀                 ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

    ╭─────────────────────────────────────────────────────────────────────╮
    │  Revolutionary MCP Server for CrewAI with Autonomous Evolution      │
    │  • Agents that evolve their personalities over time                 │
    │  • Dynamic instructions without stopping workflows                  │
    │  • Universal MCP client integration for unlimited tools             │
    │  • Self-reflecting crews that make radical autonomous decisions     │
    ╰─────────────────────────────────────────────────────────────────────╯
"""

__version__ = "0.1.0"
__author__ = "Alan"
__description__ = "MCP Server for CrewAI with autonomous evolution capabilities"

from .server import MCPCrewAIServer
from .models import EvolvingAgent, AutonomousCrew
from .evolution import EvolutionEngine

__all__ = [
    "MCPCrewAIServer",
    "EvolvingAgent", 
    "AutonomousCrew",
    "EvolutionEngine"
]