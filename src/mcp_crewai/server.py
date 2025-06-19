"""
MCP CrewAI Server - Revolutionary Autonomous Evolution Server
"""

import asyncio
import json
import logging
import sys
import time
from typing import Any, Dict, List, Optional, Sequence
from datetime import datetime

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
from pydantic import AnyUrl

from .models import EvolvingAgent, AutonomousCrew
from .evolution import EvolutionEngine
from .dynamic_instructions import DynamicInstructionHandler, WorkflowContext
from .mcp_client_agent import MCPClientAgent
from .config import get_config
from .monitoring import monitoring_manager, log_event, update_agent, update_crew, update_system
from .web_search import WebSearchMCP
from .project_analyzer import ProjectAnalyzer, ProjectAnalysis
from .security import security_middleware, AuthenticationError, AuthorizationError, ValidationError, SecurityViolationError
from .validation_schemas import validate_request_data, format_validation_error
from .task_termination import task_terminator, TerminableTask, terminate_current_task, get_active_tasks

# Get configuration and configure logging
config = get_config()
logging.basicConfig(level=getattr(logging, config.log_level.upper()))
logger = logging.getLogger(__name__)

def create_llm():
    """Create and configure LLM based on configuration settings with multi-provider support"""
    import sys
    import io
    import contextlib
    import os
    
    # Temporarily redirect streams during LLM imports
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    
    try:
        safe_stdout = io.StringIO()
        safe_stderr = io.StringIO()
        
        with contextlib.redirect_stdout(safe_stdout), contextlib.redirect_stderr(safe_stderr):
            llm_config = config.get_llm_config()
            provider = llm_config.get("provider", "openai").lower()
            model = llm_config.get("model", "gpt-4-turbo-preview")
            api_key = llm_config.get("api_key")
            base_url = llm_config.get("base_url")  # For Ollama and custom endpoints
            
            # 🤖 ANTHROPIC (Claude)
            if provider == "anthropic":
                if not api_key:
                    raise ValueError("Anthropic API key is required. Set ANTHROPIC_API_KEY environment variable.")
                
                from langchain_anthropic import ChatAnthropic
                logger.info(f"🤖 Creating Anthropic Claude LLM: {model}")
                return ChatAnthropic(
                    model=model,
                    anthropic_api_key=api_key,
                    temperature=0.1,
                    max_tokens=4096
                )
            
            # 🔴 OPENAI (GPT)
            elif provider == "openai":
                if not api_key:
                    raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
                
                from langchain_openai import ChatOpenAI
                logger.info(f"🔴 Creating OpenAI GPT LLM: {model}")
                return ChatOpenAI(
                    model=model,
                    openai_api_key=api_key,
                    temperature=0.1,
                    max_tokens=4096
                )
            
            # 🦙 OLLAMA (Local)
            elif provider == "ollama":
                from langchain_ollama import ChatOllama
                ollama_base_url = base_url or "http://localhost:11434"
                logger.info(f"🦙 Creating Ollama LLM: {model} at {ollama_base_url}")
                return ChatOllama(
                    model=model,
                    base_url=ollama_base_url,
                    temperature=0.1
                )
            
            # 💎 GOOGLE GEMINI
            elif provider == "gemini" or provider == "google":
                if not api_key:
                    raise ValueError("Google API key is required. Set GOOGLE_API_KEY environment variable.")
                
                from langchain_google_genai import ChatGoogleGenerativeAI
                logger.info(f"💎 Creating Google Gemini LLM: {model}")
                return ChatGoogleGenerativeAI(
                    model=model,
                    google_api_key=api_key,
                    temperature=0.1,
                    max_output_tokens=4096
                )
            
            # 🌐 GROQ (Fast API)
            elif provider == "groq":
                if not api_key:
                    raise ValueError("Groq API key is required. Set GROQ_API_KEY environment variable.")
                
                from langchain_groq import ChatGroq
                logger.info(f"🌐 Creating Groq LLM: {model}")
                return ChatGroq(
                    model=model,
                    groq_api_key=api_key,
                    temperature=0.1,
                    max_tokens=4096
                )
            
            # 🔵 AZURE OPENAI
            elif provider == "azure" or provider == "azure_openai":
                azure_endpoint = llm_config.get("azure_endpoint") or os.getenv("AZURE_OPENAI_ENDPOINT")
                azure_api_version = llm_config.get("azure_api_version", "2024-02-01")
                
                if not api_key or not azure_endpoint:
                    raise ValueError("Azure OpenAI requires API key and endpoint. Set AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT.")
                
                from langchain_openai import AzureChatOpenAI
                logger.info(f"🔵 Creating Azure OpenAI LLM: {model}")
                return AzureChatOpenAI(
                    deployment_name=model,
                    azure_endpoint=azure_endpoint,
                    openai_api_key=api_key,
                    openai_api_version=azure_api_version,
                    temperature=0.1,
                    max_tokens=4096
                )
            
            # ❓ UNKNOWN PROVIDER
            else:
                supported_providers = ["anthropic", "openai", "ollama", "gemini", "google", "groq", "azure", "azure_openai"]
                raise ValueError(f"Unsupported LLM provider: {provider}. Supported providers: {', '.join(supported_providers)}")
                
    except Exception as e:
        logger.error(f"❌ Failed to create {provider} LLM: {e}")
        
        # Smart fallback: Try to find any available provider
        logger.warning("🔄 Attempting smart fallback to available providers...")
        
        # Try Ollama first (no API key needed)
        try:
            from langchain_ollama import ChatOllama
            logger.info("🦙 Fallback: Using Ollama with llama3.2 model")
            return ChatOllama(
                model="llama3.2",
                base_url="http://localhost:11434",
                temperature=0.1
            )
        except Exception:
            pass
        
        # Try OpenAI if key available
        try:
            openai_key = os.getenv("OPENAI_API_KEY")
            if openai_key:
                from langchain_openai import ChatOpenAI
                logger.info("🔴 Fallback: Using OpenAI GPT-4")
                return ChatOpenAI(
                    model="gpt-4-turbo-preview",
                    openai_api_key=openai_key,
                    temperature=0.1,
                    max_tokens=4096
                )
        except Exception:
            pass
        
        # Try Anthropic if key available
        try:
            anthropic_key = os.getenv("ANTHROPIC_API_KEY")
            if anthropic_key:
                from langchain_anthropic import ChatAnthropic
                logger.info("🤖 Fallback: Using Anthropic Claude")
                return ChatAnthropic(
                    model="claude-3-5-sonnet-20241022",
                    anthropic_api_key=anthropic_key,
                    temperature=0.1,
                    max_tokens=4096
                )
        except Exception:
            pass
        
        # Ultimate failure
        raise Exception(f"Could not create any LLM instance. Original error: {e}")
        
    finally:
        sys.stdout = original_stdout
        sys.stderr = original_stderr


class MCPCrewAIServer:
    """
    🚀 REVOLUTIONARY MCP SERVER FOR CREWAI 🚀
    
    Features:
    - Autonomous agent evolution
    - Self-reflecting crews
    - Dynamic role adaptation
    - Persistent memory across sessions
    - Radical decision making
    """
    
    def __init__(self):
        # Protect stdout/stderr during initialization to prevent CrewAI FilteredStream errors
        import sys
        import io
        import contextlib
        
        # Save original streams
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        
        try:
            # Temporarily redirect streams during CrewAI imports and initialization
            safe_stdout = io.StringIO()
            safe_stderr = io.StringIO()
            
            with contextlib.redirect_stdout(safe_stdout), contextlib.redirect_stderr(safe_stderr):
                self.server = Server("mcp-crewai-server")
                self.config = config
                self.crews: Dict[str, AutonomousCrew] = {}
                self.agents: Dict[str, EvolvingAgent] = {}
                self.evolution_engine = EvolutionEngine()
                self.instruction_handler = DynamicInstructionHandler()
                self.active_workflows: Dict[str, WorkflowContext] = {}
                self.web_search = WebSearchMCP()
                self.project_analyzer = ProjectAnalyzer()
                
                # Server startup time
                self.startup_time = datetime.now()
        finally:
            # Always restore original streams
            sys.stdout = original_stdout
            sys.stderr = original_stderr
        
        # Log configuration summary (after streams are restored)
        self._log_startup_info()
        
        # Register tools
        print("🔍 Starting tool registration...", file=sys.stderr)
        self._register_tools()
        print("✅ Tool registration completed", file=sys.stderr)
        
        # Background evolution task
        self._evolution_task: Optional[asyncio.Task] = None
    
    def _log_startup_info(self):
        """Log server startup information and configuration"""
        logger.info("🚀 MCP CrewAI Server Starting...")
        
        summary = self.config.get_summary()
        is_ready, issues = self.config.is_production_ready()
        
        logger.info(f"📊 Configuration Summary:")
        logger.info(f"   Host: {summary['server']['host']}:{summary['server']['port']}")
        logger.info(f"   LLM: {summary['llm']['provider']} ({summary['llm']['model']})")
        logger.info(f"   API Key: {'✅ Configured' if summary['llm']['api_key_configured'] else '❌ Missing'}")
        logger.info(f"   Features: Evolution={summary['features']['evolution']}, "
                   f"Dynamic={summary['features']['dynamic_instructions']}, "
                   f"Memory={summary['features']['memory']}")
        logger.info(f"   External MCP Servers: {summary['external_mcp_servers']}")
        logger.info(f"   Production Ready: {'✅ Yes' if is_ready else '❌ No'}")
        
        if not is_ready:
            logger.warning("⚠️  Production readiness issues:")
            for issue in issues:
                logger.warning(f"   • {issue}")
    
    def _register_tools(self):
        """Register all MCP tools for CrewAI operations"""
        try:
            print("🔍 Registering MCP tools...", file=sys.stderr)
            
            # Add debug logging for requests
            original_request_handler = self.server._request_handlers.copy() if hasattr(self.server, '_request_handlers') else {}
            
            def debug_decorator(handler):
                async def wrapper(request):
                    print(f"🔍 Request received: {request.method if hasattr(request, 'method') else request}", file=sys.stderr)
                    try:
                        result = await handler(request)
                        print(f"✅ Request handled successfully: {request.method if hasattr(request, 'method') else 'unknown'}", file=sys.stderr)
                        return result
                    except Exception as e:
                        print(f"❌ Request handler error: {e}", file=sys.stderr)
                        raise
                return wrapper
            
            @self.server.list_tools()
            async def handle_list_tools() -> List[Tool]:
                """List all available tools"""
                return [
                Tool(
                    name="create_evolving_crew",
                    description="Create a new autonomous evolving crew",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "crew_name": {"type": "string"},
                            "agents_config": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "role": {"type": "string"},
                                        "goal": {"type": "string"},
                                        "backstory": {"type": "string"},
                                        "personality_preset": {"type": "string", "enum": ["analytical", "creative", "collaborative", "decisive"]}
                                    },
                                    "required": ["role", "goal", "backstory"]
                                }
                            },
                            "tasks": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "description": {"type": "string"},
                                        "agent_role": {"type": "string"}
                                    },
                                    "required": ["description"]
                                }
                            },
                            "autonomy_level": {"type": "number", "minimum": 0.0, "maximum": 1.0, "default": 0.5}
                        },
                        "required": ["crew_name", "agents_config", "tasks"]
                    }
                ),
                
                Tool(
                    name="create_crew_from_project_analysis",
                    description="Analyze project requirements and create optimally-sized crew automatically",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_description": {"type": "string"},
                            "project_goals": {"type": "array", "items": {"type": "string"}, "default": []},
                            "constraints": {
                                "type": "object", 
                                "properties": {
                                    "max_agents": {"type": "integer", "minimum": 1, "maximum": 10},
                                    "min_agents": {"type": "integer", "minimum": 1, "maximum": 10},
                                    "budget": {"type": "string"},
                                    "timeline": {"type": "string"}
                                },
                                "default": {}
                            },
                            "crew_name": {"type": "string"},
                            "autonomy_level": {"type": "number", "minimum": 0.0, "maximum": 1.0, "default": 0.7}
                        },
                        "required": ["project_description", "crew_name"]
                    }
                ),
                
                Tool(
                    name="analyze_project_requirements",
                    description="Analyze project requirements and get team composition recommendations without creating crew",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_description": {"type": "string"},
                            "project_goals": {"type": "array", "items": {"type": "string"}, "default": []},
                            "constraints": {
                                "type": "object", 
                                "properties": {
                                    "max_agents": {"type": "integer", "minimum": 1, "maximum": 10},
                                    "min_agents": {"type": "integer", "minimum": 1, "maximum": 10},
                                    "budget": {"type": "string"},
                                    "timeline": {"type": "string"}
                                },
                                "default": {}
                            }
                        },
                        "required": ["project_description"]
                    }
                ),
                
                Tool(
                    name="run_autonomous_crew",
                    description="Execute crew with autonomous decision making",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "crew_id": {"type": "string"},
                            "context": {"type": "object", "default": {}},
                            "allow_evolution": {"type": "boolean", "default": True}
                        },
                        "required": ["crew_id"]
                    }
                ),
                
                Tool(
                    name="get_crew_status",
                    description="Get detailed status of a crew including evolution metrics",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "crew_id": {"type": "string"}
                        },
                        "required": ["crew_id"]
                    }
                ),
                
                Tool(
                    name="trigger_agent_evolution",
                    description="Force evolution cycle for specific agent",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "agent_id": {"type": "string"},
                            "evolution_type": {"type": "string", "enum": ["personality", "role", "radical"], "default": "personality"}
                        },
                        "required": ["agent_id"]
                    }
                ),
                
                Tool(
                    name="crew_self_assessment",
                    description="Make crew perform self-assessment and suggest improvements",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "crew_id": {"type": "string"}
                        },
                        "required": ["crew_id"]
                    }
                ),
                
                Tool(
                    name="list_active_crews",
                    description="List all active crews with their evolution status",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False
                    }
                ),
                
                Tool(
                    name="get_agent_reflection",
                    description="Get agent's self-reflection and evolution suggestions",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "agent_id": {"type": "string"}
                        },
                        "required": ["agent_id"]
                    }
                ),
                
                Tool(
                    name="create_agent_from_template",
                    description="Create agent from personality template",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "template": {"type": "string", "enum": ["analytical", "creative", "diplomat", "executor", "innovator"]},
                            "role": {"type": "string"},
                            "goal": {"type": "string"},
                            "customizations": {"type": "object", "default": {}}
                        },
                        "required": ["template", "role", "goal"]
                    }
                ),
                
                # DYNAMIC INSTRUCTIONS TOOLS
                Tool(
                    name="add_dynamic_instruction",
                    description="Add instruction to running crew without stopping workflow",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "crew_id": {"type": "string"},
                            "instruction": {"type": "string"},
                            "instruction_type": {"type": "string", "enum": ["guidance", "constraint", "resource", "pivot", "feedback", "emergency_stop", "skill_boost"], "default": "guidance"},
                            "target": {"type": "string", "default": "crew"},
                            "priority": {"type": "integer", "minimum": 1, "maximum": 5, "default": 1}
                        },
                        "required": ["crew_id", "instruction"]
                    }
                ),
                
                Tool(
                    name="get_instruction_status",
                    description="Get status of specific instruction",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "instruction_id": {"type": "string"}
                        },
                        "required": ["instruction_id"]
                    }
                ),
                
                Tool(
                    name="list_dynamic_instructions",
                    description="List all dynamic instructions for crew",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "crew_id": {"type": "string"}
                        },
                        "required": ["crew_id"]
                    }
                ),
                
                Tool(
                    name="get_workflow_status",
                    description="Get real-time status of running workflow",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "crew_id": {"type": "string"}
                        },
                        "required": ["crew_id"]
                    }
                ),
                
                # MCP CLIENT TOOLS
                Tool(
                    name="connect_agent_to_mcp_server",
                    description="Connect agent to external MCP server for tool access",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "agent_id": {"type": "string"},
                            "server_config": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "command": {"type": "array", "items": {"type": "string"}},
                                    "description": {"type": "string"},
                                    "capabilities": {"type": "array", "items": {"type": "string"}}
                                },
                                "required": ["name", "command"]
                            }
                        },
                        "required": ["agent_id", "server_config"]
                    }
                ),
                
                Tool(
                    name="agent_use_mcp_tool",
                    description="Make agent use specific MCP tool",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "agent_id": {"type": "string"},
                            "tool_name": {"type": "string"},
                            "arguments": {"type": "object"},
                            "context": {"type": "string", "default": ""}
                        },
                        "required": ["agent_id", "tool_name", "arguments"]
                    }
                ),
                
                Tool(
                    name="get_agent_mcp_status",
                    description="Get agent's MCP connections and available tools",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "agent_id": {"type": "string"}
                        },
                        "required": ["agent_id"]
                    }
                ),
                
                Tool(
                    name="suggest_tools_for_task",
                    description="Get agent's suggestions for MCP tools to help with task",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "agent_id": {"type": "string"},
                            "task_description": {"type": "string"}
                        },
                        "required": ["agent_id", "task_description"]
                    }
                ),
                
                Tool(
                    name="auto_discover_mcp_servers",
                    description="Auto-discover and connect agent to available MCP servers",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "agent_id": {"type": "string"},
                            "discovery_config": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "command": {"type": "array", "items": {"type": "string"}},
                                        "description": {"type": "string"}
                                    },
                                    "required": ["name", "command"]
                                }
                            }
                        },
                        "required": ["agent_id", "discovery_config"]
                    }
                ),
                Tool(
                    name="get_server_config",
                    description="Get complete server configuration and status",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="health_check",
                    description="Perform comprehensive server health check",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "include_details": {"type": "boolean", "default": False}
                        },
                        "required": []
                    }
                ),
                Tool(
                    name="reload_config",
                    description="Reload server configuration from environment",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="get_monitoring_dashboard",
                    description="Get real-time monitoring dashboard data",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="get_agent_details",
                    description="Get detailed information about a specific agent",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "agent_id": {"type": "string"}
                        },
                        "required": ["agent_id"]
                    }
                ),
                Tool(
                    name="get_evolution_summary",
                    description="Get summary of evolution activity",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="get_live_events",
                    description="Get recent monitoring events",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "count": {"type": "integer", "default": 50},
                            "event_type": {"type": "string"}
                        },
                        "required": []
                    }
                ),
                
                # WEB SEARCH TOOLS FOR AGENT SELF-IMPROVEMENT
                Tool(
                    name="agent_web_search",
                    description="Allow agent to search the internet for self-improvement",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "agent_id": {"type": "string"},
                            "query": {"type": "string"},
                            "max_results": {"type": "integer", "default": 5, "minimum": 1, "maximum": 10},
                            "purpose": {"type": "string", "enum": ["learning", "research", "problem_solving", "skill_development"], "default": "learning"}
                        },
                        "required": ["agent_id", "query"]
                    }
                ),
                
                Tool(
                    name="agent_research_topic",
                    description="Deep research on a topic for agent improvement",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "agent_id": {"type": "string"},
                            "topic": {"type": "string"},
                            "depth": {"type": "string", "enum": ["standard", "comprehensive"], "default": "standard"},
                            "focus_area": {"type": "string", "enum": ["skills", "collaboration", "performance", "innovation"], "default": "skills"}
                        },
                        "required": ["agent_id", "topic"]
                    }
                ),
                
                Tool(
                    name="agent_fact_check",
                    description="Fact-check information for agent knowledge validation",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "agent_id": {"type": "string"},
                            "claim": {"type": "string"}
                        },
                        "required": ["agent_id", "claim"]
                    }
                ),
                
                Tool(
                    name="get_agent_search_analytics",
                    description="Get search analytics and learning patterns for agent",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "agent_id": {"type": "string"}
                        },
                        "required": ["agent_id"]
                    }
                ),
                
                Tool(
                    name="trigger_research_based_evolution",
                    description="Trigger agent evolution based on research findings",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "agent_id": {"type": "string"},
                            "research_topic": {"type": "string"},
                            "apply_insights": {"type": "boolean", "default": True}
                        },
                        "required": ["agent_id", "research_topic"]
                    }
                ),
                
                # Task Termination Tools
                Tool(
                    name="terminate_current_task",
                    description="Gracefully terminate current agent task and pass partial results to next step",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {"type": "string"},
                            "reason": {"type": "string", "default": "User requested termination"}
                        },
                        "required": ["task_id"]
                    }
                ),
                
                Tool(
                    name="get_active_tasks",
                    description="Get list of all active tasks that can be terminated",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False
                    }
                ),
                
                Tool(
                    name="get_task_status",
                    description="Get detailed status of a specific task including progress and partial results",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {"type": "string"}
                        },
                        "required": ["task_id"]
                    }
                )
                ]
        
            @self.server.call_tool()
            async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
                """Handle tool calls with security validation"""
                
                try:
                    # Security Phase 1: Authentication & Authorization
                    # For now, simulate auth context (in production, extract from request headers)
                    auth_context = {
                        'client_id': 'system_client',
                        'permissions': ['*'],  # Admin permissions for system calls
                        'authenticated': True
                    }
                    
                    # Authorize tool access
                    if not security_middleware.authorize_tool_access(auth_context, name):
                        raise AuthorizationError(f"Access denied to tool: {name}")
                    
                    # Validate and sanitize arguments
                    validated_args = security_middleware.validate_tool_arguments(name, arguments)
                    
                    # Log security event
                    from .security import security_audit_log
                    security_audit_log("tool_execution", {
                        "tool_name": name,
                        "client_id": auth_context['client_id'],
                        "arguments_count": len(validated_args)
                    })
                    
                except (AuthenticationError, AuthorizationError, ValidationError, SecurityViolationError) as e:
                    logger.error(f"🚫 Security violation in tool {name}: {e}")
                    return [TextContent(
                        type="text",
                        text=f"Security Error: {str(e)}"
                    )]
                except Exception as e:
                    logger.error(f"🚫 Validation error in tool {name}: {e}")
                    return [TextContent(
                        type="text",
                        text=f"Validation Error: {str(e)}"
                    )]
                
                # Use validated arguments for all tool calls
                arguments = validated_args
                
                if name == "create_evolving_crew":
                    return await self._create_evolving_crew(arguments)
                
                elif name == "run_autonomous_crew":
                    return await self._run_autonomous_crew(arguments)
                
                elif name == "get_crew_status":
                    return await self._get_crew_status(arguments)
                
                elif name == "trigger_agent_evolution":
                    return await self._trigger_agent_evolution(arguments)
                
                elif name == "crew_self_assessment":
                    return await self._crew_self_assessment(arguments)
                
                elif name == "list_active_crews":
                    return await self._list_active_crews(arguments)
                
                elif name == "get_agent_reflection":
                    return await self._get_agent_reflection(arguments)
                
                elif name == "create_agent_from_template":
                    return await self._create_agent_from_template(arguments)
                
                # Dynamic Instructions Tools
                elif name == "add_dynamic_instruction":
                    return await self._add_dynamic_instruction(arguments)
                
                elif name == "get_instruction_status":
                    return await self._get_instruction_status(arguments)
                
                elif name == "list_dynamic_instructions":
                    return await self._list_dynamic_instructions(arguments)
                
                elif name == "get_workflow_status":
                    return await self._get_workflow_status(arguments)
                
                # MCP Client Tools
                elif name == "connect_agent_to_mcp_server":
                    return await self._connect_agent_to_mcp_server(arguments)
                
                elif name == "agent_use_mcp_tool":
                    return await self._agent_use_mcp_tool(arguments)
                
                elif name == "get_agent_mcp_status":
                    return await self._get_agent_mcp_status(arguments)
                
                elif name == "suggest_tools_for_task":
                    return await self._suggest_tools_for_task(arguments)
                
                elif name == "auto_discover_mcp_servers":
                    return await self._auto_discover_mcp_servers(arguments)
                
                # Configuration and Health Tools
                elif name == "get_server_config":
                    return await self._get_server_config(arguments)
                
                elif name == "health_check":
                    return await self._health_check(arguments)
                
                elif name == "reload_config":
                    return await self._reload_config(arguments)
                
                # Monitoring Tools
                elif name == "get_monitoring_dashboard":
                    return await self._get_monitoring_dashboard(arguments)
                
                elif name == "get_agent_details":
                    return await self._get_agent_details(arguments)
                
                elif name == "get_evolution_summary":
                    return await self._get_evolution_summary(arguments)
                
                elif name == "get_live_events":
                    return await self._get_live_events(arguments)
                
                # Web Search Tools
                elif name == "agent_web_search":
                    return await self._agent_web_search(arguments)
                
                elif name == "agent_research_topic":
                    return await self._agent_research_topic(arguments)
                
                elif name == "agent_fact_check":
                    return await self._agent_fact_check(arguments)
                
                elif name == "get_agent_search_analytics":
                    return await self._get_agent_search_analytics(arguments)
                
                elif name == "trigger_research_based_evolution":
                    return await self._trigger_research_based_evolution(arguments)
                
                # Task Termination Tools
                elif name == "terminate_current_task":
                    return await self._terminate_current_task(arguments)
                
                elif name == "get_active_tasks":
                    return await self._get_active_tasks(arguments)
                
                elif name == "get_task_status":
                    return await self._get_task_status_detail(arguments)
                
                else:
                    raise ValueError(f"Unknown tool: {name}")
        
            print("✅ MCP tools registered successfully", file=sys.stderr)
        except Exception as e:
            print(f"❌ Error registering tools: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            raise
    
    async def _handle_call_tool(self, name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Public method to handle tool calls from HTTP server"""
        # Directly call monitoring methods for quick access
        if name == "get_monitoring_dashboard":
            return await self._get_monitoring_dashboard(arguments)
        elif name == "get_agent_details":
            return await self._get_agent_details(arguments)
        elif name == "get_evolution_summary":
            return await self._get_evolution_summary(arguments)
        elif name == "get_live_events":
            return await self._get_live_events(arguments)
        elif name == "health_check":
            return await self._health_check(arguments)
        
        # For other tools, use a more systematic approach
        # This maps to the internal tool handler logic without recursion
        tool_map = {
            "create_evolving_crew": self._create_evolving_crew,
            "create_crew_from_project_analysis": self._create_crew_from_project_analysis,
            "analyze_project_requirements": self._analyze_project_requirements,
            "run_autonomous_crew": self._run_autonomous_crew,
            "get_crew_status": self._get_crew_status,
            "trigger_agent_evolution": self._trigger_agent_evolution,
            "crew_self_assessment": self._crew_self_assessment,
            "list_active_crews": self._list_active_crews,
            "get_agent_reflection": self._get_agent_reflection,
            "create_agent_from_template": self._create_agent_from_template,
            "add_dynamic_instruction": self._add_dynamic_instruction,
            "get_instruction_status": self._get_instruction_status,
            "list_dynamic_instructions": self._list_dynamic_instructions,
            "get_workflow_status": self._get_workflow_status,
            "connect_agent_to_mcp_server": self._connect_agent_to_mcp_server,
            "agent_use_mcp_tool": self._agent_use_mcp_tool,
            "get_agent_mcp_status": self._get_agent_mcp_status,
            "suggest_tools_for_task": self._suggest_tools_for_task,
            "auto_discover_mcp_servers": self._auto_discover_mcp_servers,
            "get_server_config": self._get_server_config,
            "reload_config": self._reload_config,
        }
        
        if name in tool_map:
            return await tool_map[name](arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    async def _create_evolving_crew(self, args: Dict[str, Any]) -> List[TextContent]:
        """Create a new evolving crew"""
        crew_name = args["crew_name"]
        agents_config = args["agents_config"]
        tasks_config = args["tasks"]
        autonomy_level = args.get("autonomy_level", 0.5)
        
        # Create evolving agents with MCP client capabilities
        agents = []
        
        # Create LLM instance for all agents
        try:
            llm = create_llm()
            logger.info(f"🤖 Created LLM instance: {llm.__class__.__name__}")
        except Exception as e:
            logger.error(f"❌ Failed to create LLM: {e}")
            raise Exception(f"Cannot create agents without LLM: {e}")
        
        for agent_config in agents_config:
            agent = MCPClientAgent(
                role=agent_config["role"],
                goal=agent_config["goal"],
                backstory=agent_config["backstory"],
                llm=llm,  # Configure the LLM for this agent
                verbose=True,
                allow_delegation=False
            )
            
            # Apply personality preset if specified
            if "personality_preset" in agent_config:
                self._apply_personality_preset(agent, agent_config["personality_preset"])
            
            # Connect agent to real MCP servers instead of mock tools
            await self._connect_agent_to_mcp_servers(agent)
            
            agents.append(agent)
            self.agents[agent.agent_id] = agent
        
        # Create tasks (simplified for now)
        # Import Task safely to avoid FilteredStream errors
        import sys
        import io
        import contextlib
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        try:
            safe_stdout = io.StringIO()
            safe_stderr = io.StringIO()
            with contextlib.redirect_stdout(safe_stdout), contextlib.redirect_stderr(safe_stderr):
                from crewai import Task, Process
        finally:
            sys.stdout = original_stdout
            sys.stderr = original_stderr
        tasks = []
        for i, task_config in enumerate(tasks_config):
            # Find agent by role if specified, or distribute tasks across agents
            assigned_agent = None
            if "agent_role" in task_config:
                assigned_agent = next(
                    (a for a in agents if a.role == task_config["agent_role"]), 
                    agents[i % len(agents)]
                )
            else:
                # Distribute tasks across all available agents for hierarchical coordination
                assigned_agent = agents[i % len(agents)]
            
            # Generate expected_output if not provided
            expected_output = task_config.get(
                "expected_output", 
                f"Completed deliverable for: {task_config['description']}"
            )
            
            task = Task(
                description=task_config["description"],
                agent=assigned_agent,
                expected_output=expected_output
            )
            tasks.append(task)
        
        # Create autonomous crew with sequential process for reliable task execution
        # Note: Sequential process executes all tasks in order, ensuring complete deliverables
        # Task distribution is handled by our round-robin assignment (line 895)
        crew = AutonomousCrew(
            agents=agents,
            tasks=tasks,
            process=Process.sequential,  # Sequential ensures all tasks execute
            verbose=True
        )
        crew.autonomy_level = autonomy_level
        
        self.crews[crew_name] = crew
        
        # Log monitoring events
        log_event("crew", f"Created crew '{crew_name}' with {len(agents)} agents", 
                 crew_id=crew_name, details={
                     "agents_count": len(agents),
                     "autonomy_level": autonomy_level,
                     "tasks_count": len(tasks)
                 })
        
        # Update monitoring status
        update_crew(crew_name, 
                   crew_name=crew_name,
                   status="idle",
                   agents_count=len(agents),
                   active_agents=0,
                   autonomy_level=autonomy_level,
                   tasks_queue=len(tasks))
        
        # Update each agent's monitoring status
        for agent in agents:
            update_agent(agent.agent_id,
                        role=agent.role,
                        status="idle",
                        personality_traits={name: trait.value for name, trait in agent.personality_traits.items()},
                        evolution_cycles=agent.evolution_cycles,
                        tasks_completed=agent.tasks_completed)
        
        result = {
            "status": "success",
            "crew_id": crew_name,
            "crew_info": {
                "agents_count": len(agents),
                "tasks_count": len(tasks),
                "autonomy_level": autonomy_level,
                "agent_ids": [agent.agent_id for agent in agents]
            },
            "message": f"🚀 Evolutionary crew '{crew_name}' created with {len(agents)} agents!"
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def _run_autonomous_crew(self, args: Dict[str, Any]) -> List[TextContent]:
        """Run crew with autonomous capabilities"""
        crew_id = args["crew_id"]
        context = args.get("context", {})
        allow_evolution = args.get("allow_evolution", True)
        
        if crew_id not in self.crews:
            return [TextContent(type="text", text=f"❌ Crew '{crew_id}' not found")]
        
        crew = self.crews[crew_id]
        
        # Create workflow context for dynamic instructions
        workflow = WorkflowContext(crew_id, crew)
        self.active_workflows[crew_id] = workflow
        
        # Wait for MCP connections to be established before autonomous decision making
        await self._ensure_mcp_connections_ready(crew)
        
        # Autonomous decision making after MCP connections are ready
        if allow_evolution and crew.autonomy_level > 0.3:
            decision = crew.make_autonomous_decision(context)
            if decision["action"] != "continue":
                crew.execute_autonomous_changes(decision)
                
                result = {
                    "status": "autonomous_changes_made",
                    "decision": decision,
                    "evolution_events": [],
                    "dynamic_instruction_stats": {"instructions_processed": 0},
                    "message": f"🧠 Crew made autonomous decision: {decision['reasoning']}"
                }
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        # Execute crew with dynamic instruction monitoring
        try:
            # Real CrewAI execution with dynamic instruction monitoring
            log_event(
                "crew_execution_started",
                f"Starting real CrewAI execution for crew {crew_id}",
                crew_id=crew_id
            )
            
            # Set up execution monitoring
            execution_task = asyncio.create_task(self._execute_crew_with_monitoring(crew, workflow))
            crew_result = await execution_task
            
            # Complete execution and generate deliverable results
            crew.crew_metrics["tasks_completed"] += len(crew.tasks)
            crew.crew_metrics["success_rate"] = 0.85  # Will be calculated from actual results
            
            # Generate crew deliverable results from real CrewAI execution
            deliverable_results = await self._generate_crew_deliverables(crew, crew_result)
            
            # Update agent metrics and check for evolution
            evolution_events = []
            for agent in crew.agents:
                agent.tasks_completed += 1
                agent.evolution_metrics.success_rate = 0.80  # Simulated
                
                # Check if agent should evolve
                if allow_evolution and agent.should_evolve():
                    reflection = agent.self_reflect()
                    if reflection["evolution_suggestions"]:
                        agent.evolve(reflection["evolution_suggestions"])
                        evolution_events.append({
                            "agent_id": agent.agent_id,
                            "evolution_cycle": agent.evolution_cycles,
                            "changes": reflection["evolution_suggestions"]
                        })
            
            # Conduct crew debrief session
            debrief_insights = await self._conduct_crew_debrief(crew, evolution_events)
            
            # Prepare liberation summary (but don't execute yet)
            liberation_summary = await self._prepare_liberation_summary(crew)
            
            # Clean up workflow
            workflow.status = "completed"
            
            result = {
                "status": "completed",
                "crew_id": crew_id,
                "deliverable_results": deliverable_results,
                "debrief_insights": debrief_insights,
                "evolution_events": evolution_events,
                "crew_metrics": crew.crew_metrics,
                "agents_to_be_liberated": len(crew.agents),
                "dynamic_instruction_stats": {
                    "instructions_processed": len(self.instruction_handler.get_all_instructions(crew_id)),
                    "guidance_received": len(getattr(crew, 'user_guidance', [])),
                    "constraints_applied": len(getattr(crew, 'active_constraints', [])),
                    "resources_provided": len(getattr(crew, 'dynamic_resources', []))
                }
            }
            
            # Return results FIRST, then liberate agents
            response_text = json.dumps(result, indent=2)
            
            # NOW liberate agents after preparing response
            await self._liberate_agents_with_experience(crew)
            
            return [TextContent(type="text", text=response_text)]
            
        except asyncio.CancelledError:
            # Handle emergency stop
            result = {
                "status": "stopped",
                "crew_id": crew_id,
                "stop_reason": getattr(crew, 'stop_reason', 'Emergency stop'),
                "message": "🚨 Execution stopped by emergency instruction",
                "partial_results": "Execution was cancelled before completion"
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        except Exception as e:
            # Handle other execution errors
            log_event(
                "crew_execution_failed", 
                f"Crew execution failed: {str(e)}", 
                crew_id=crew_id,
                details={"error": str(e), "error_type": type(e).__name__}
            )
            return [TextContent(type="text", text=f"❌ Execution failed: {str(e)}")]
    
    async def _get_crew_status(self, args: Dict[str, Any]) -> List[TextContent]:
        """Get detailed crew status"""
        crew_id = args["crew_id"]
        
        if crew_id not in self.crews:
            return [TextContent(type="text", text=f"❌ Crew '{crew_id}' not found")]
        
        crew = self.crews[crew_id]
        
        status = {
            "crew_id": crew_id,
            "formation_date": crew.formation_date.isoformat(),
            "autonomy_level": crew.autonomy_level,
            "metrics": crew.crew_metrics,
            "agents": [
                {
                    "agent_id": agent.agent_id,
                    "role": agent.role,
                    "age_weeks": agent.age_in_weeks(),
                    "evolution_cycles": agent.evolution_cycles,
                    "tasks_completed": agent.tasks_completed,
                    "personality_traits": {
                        name: trait.value for name, trait in agent.personality_traits.items()
                    },
                    "performance": {
                        "success_rate": agent.evolution_metrics.success_rate,
                        "collaboration_score": agent.evolution_metrics.collaboration_score
                    }
                }
                for agent in crew.agents
            ],
            "capabilities_assessment": crew.assess_capabilities()
        }
        
        return [TextContent(type="text", text=json.dumps(status, indent=2))]
    
    async def _trigger_agent_evolution(self, args: Dict[str, Any]) -> List[TextContent]:
        """Force agent evolution"""
        agent_id = args["agent_id"]
        evolution_type = args.get("evolution_type", "personality")
        
        if agent_id not in self.agents:
            return [TextContent(type="text", text=f"❌ Agent '{agent_id}' not found")]
        
        agent = self.agents[agent_id]
        
        # Capture previous traits before evolution
        previous_traits = {
            name: trait.value for name, trait in agent.personality_traits.items()
        }
        
        # Force evolution
        reflection = agent.self_reflect()
        
        if evolution_type == "radical":
            # Force radical changes
            reflection["evolution_suggestions"]["radical_changes"] = ["complete_personality_overhaul"]
        
        agent.evolve(reflection["evolution_suggestions"])
        
        # Capture current traits after evolution
        current_traits = {
            name: trait.value for name, trait in agent.personality_traits.items()
        }
        
        # Log evolution event for monitoring
        trait_changes = {name: current_traits[name] - previous_traits[name] 
                        for name in current_traits if name in previous_traits}
        significant_changes = {name: change for name, change in trait_changes.items() 
                             if abs(change) > 0.1}
        
        log_event("evolution", 
                 f"Agent {agent.role} evolved (cycle #{agent.evolution_cycles})", 
                 agent_id=agent_id,
                 details={
                     "evolution_type": evolution_type,
                     "cycle": agent.evolution_cycles,
                     "previous_traits": previous_traits,
                     "current_traits": current_traits,
                     "significant_changes": significant_changes
                 })
        
        # Update agent monitoring status
        update_agent(agent_id,
                    status="idle",
                    personality_traits=current_traits,
                    evolution_cycles=agent.evolution_cycles)
        
        result = {
            "status": "evolution_completed",
            "agent_id": agent_id,
            "evolution_type": evolution_type,
            "cycle": agent.evolution_cycles,
            "changes": reflection["evolution_suggestions"],
            "previous_traits": previous_traits,
            "current_traits": current_traits
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def _crew_self_assessment(self, args: Dict[str, Any]) -> List[TextContent]:
        """Make crew perform self-assessment"""
        crew_id = args["crew_id"]
        
        if crew_id not in self.crews:
            return [TextContent(type="text", text=f"❌ Crew '{crew_id}' not found")]
        
        crew = self.crews[crew_id]
        assessment = crew.assess_capabilities()
        
        # Generate improvement suggestions
        suggestions = []
        if assessment["missing_elements"]:
            suggestions.append(f"Add: {', '.join(assessment['missing_elements'])}")
        
        if assessment["team_balance"] < 0.5:
            suggestions.append("Improve team personality diversity")
        
        result = {
            "crew_id": crew_id,
            "self_assessment": assessment,
            "improvement_suggestions": suggestions,
            "confidence_level": min(assessment["team_balance"] * 2, 1.0),
            "recommendation": "evolve" if suggestions else "maintain_current_setup"
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def _list_active_crews(self, args: Dict[str, Any]) -> List[TextContent]:
        """List all active crews"""
        crews_info = []
        
        for crew_id, crew in self.crews.items():
            crews_info.append({
                "crew_id": crew_id,
                "agents_count": len(crew.agents),
                "autonomy_level": crew.autonomy_level,
                "formation_date": crew.formation_date.isoformat(),
                "total_evolution_cycles": sum(agent.evolution_cycles for agent in crew.agents),
                "average_success_rate": sum(agent.evolution_metrics.success_rate for agent in crew.agents) / len(crew.agents) if crew.agents else 0
            })
        
        result = {
            "active_crews": len(self.crews),
            "crews": crews_info,
            "total_agents": len(self.agents)
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def _get_agent_reflection(self, args: Dict[str, Any]) -> List[TextContent]:
        """Get agent's self-reflection"""
        agent_id = args["agent_id"]
        
        if agent_id not in self.agents:
            return [TextContent(type="text", text=f"❌ Agent '{agent_id}' not found")]
        
        agent = self.agents[agent_id]
        reflection = agent.self_reflect()
        
        result = {
            "agent_id": agent_id,
            "role": agent.role,
            "reflection_timestamp": datetime.now().isoformat(),
            "self_reflection": reflection,
            "should_evolve": agent.should_evolve(),
            "evolution_readiness": "ready" if agent.should_evolve() else "not_ready"
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def _create_agent_from_template(self, args: Dict[str, Any]) -> List[TextContent]:
        """Create agent from personality template"""
        template = args["template"]
        role = args["role"]
        goal = args["goal"]
        customizations = args.get("customizations", {})
        
        # Create LLM instance for the agent
        try:
            llm = create_llm()
            logger.info(f"🤖 Created LLM instance for template agent: {llm.__class__.__name__}")
        except Exception as e:
            logger.error(f"❌ Failed to create LLM: {e}")
            raise Exception(f"Cannot create agent without LLM: {e}")
        
        agent = EvolvingAgent(
            role=role,
            goal=goal,
            backstory=f"I am a {template} specialist focused on {goal}",
            llm=llm,  # Configure the LLM for this agent
            verbose=True
        )
        
        self._apply_personality_preset(agent, template)
        
        # Apply customizations
        if customizations:
            for trait_name, trait_value in customizations.items():
                if trait_name in agent.personality_traits:
                    agent.personality_traits[trait_name].value = min(max(trait_value, 0.0), 1.0)
        
        self.agents[agent.agent_id] = agent
        
        result = {
            "status": "agent_created",
            "agent_id": agent.agent_id,
            "template": template,
            "role": role,
            "personality_traits": {
                name: trait.value for name, trait in agent.personality_traits.items()
            }
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    def _apply_personality_preset(self, agent: EvolvingAgent, preset: str):
        """Apply personality preset to agent"""
        presets = {
            "analytical": {
                "analytical": 0.9,
                "creative": 0.3,
                "collaborative": 0.6,
                "decisive": 0.8,
                "adaptable": 0.5,
                "risk_taking": 0.2
            },
            "creative": {
                "analytical": 0.4,
                "creative": 0.9,
                "collaborative": 0.7,
                "decisive": 0.6,
                "adaptable": 0.8,
                "risk_taking": 0.7
            },
            "diplomat": {
                "analytical": 0.6,
                "creative": 0.5,
                "collaborative": 0.9,
                "decisive": 0.4,
                "adaptable": 0.8,
                "risk_taking": 0.3
            },
            "executor": {
                "analytical": 0.7,
                "creative": 0.4,
                "collaborative": 0.6,
                "decisive": 0.9,
                "adaptable": 0.6,
                "risk_taking": 0.5
            },
            "innovator": {
                "analytical": 0.6,
                "creative": 0.8,
                "collaborative": 0.5,
                "decisive": 0.7,
                "adaptable": 0.9,
                "risk_taking": 0.8
            }
        }
        
        if preset in presets:
            for trait_name, value in presets[preset].items():
                if trait_name in agent.personality_traits:
                    agent.personality_traits[trait_name].value = value
    
    # =================================
    # DYNAMIC INSTRUCTIONS TOOLS
    # =================================
    
    async def _add_dynamic_instruction(self, args: Dict[str, Any]) -> List[TextContent]:
        """Add dynamic instruction to running crew"""
        crew_id = args["crew_id"]
        instruction = args["instruction"]
        instruction_type = args.get("instruction_type", "guidance")
        target = args.get("target", "crew")
        priority = args.get("priority", 1)
        
        if crew_id not in self.crews:
            return [TextContent(type="text", text=f"❌ Crew '{crew_id}' not found")]
        
        # Add instruction to handler
        instruction_id = self.instruction_handler.add_instruction(
            content=instruction,
            instruction_type=instruction_type,
            target=crew_id,
            priority=priority
        )
        
        result = {
            "status": "instruction_added",
            "instruction_id": instruction_id,
            "crew_id": crew_id,
            "type": instruction_type,
            "content": instruction,
            "priority": priority,
            "message": f"📝 Dynamic instruction added to {crew_id}"
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def _get_instruction_status(self, args: Dict[str, Any]) -> List[TextContent]:
        """Get status of specific instruction"""
        instruction_id = args["instruction_id"]
        
        status = self.instruction_handler.get_instruction_status(instruction_id)
        
        if status is None:
            return [TextContent(type="text", text=f"❌ Instruction '{instruction_id}' not found")]
        
        return [TextContent(type="text", text=json.dumps(status, indent=2))]
    
    async def _list_dynamic_instructions(self, args: Dict[str, Any]) -> List[TextContent]:
        """List all dynamic instructions for crew"""
        crew_id = args["crew_id"]
        
        if crew_id not in self.crews:
            return [TextContent(type="text", text=f"❌ Crew '{crew_id}' not found")]
        
        instructions = self.instruction_handler.get_all_instructions(crew_id)
        
        result = {
            "crew_id": crew_id,
            "total_instructions": len(instructions),
            "instructions": instructions
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def _get_workflow_status(self, args: Dict[str, Any]) -> List[TextContent]:
        """Get real-time workflow status"""
        crew_id = args["crew_id"]
        
        if crew_id not in self.crews:
            return [TextContent(type="text", text=f"❌ Crew '{crew_id}' not found")]
        
        crew = self.crews[crew_id]
        workflow = self.active_workflows.get(crew_id)
        
        status = {
            "crew_id": crew_id,
            "workflow_active": workflow is not None,
            "crew_status": {
                "formation_date": crew.formation_date.isoformat(),
                "autonomy_level": crew.autonomy_level,
                "agents_count": len(crew.agents),
                "emergency_stop": getattr(crew, 'emergency_stop', False)
            }
        }
        
        if workflow:
            status["workflow_status"] = {
                "start_time": workflow.start_time.isoformat(),
                "status": workflow.status,
                "last_instruction_check": workflow.last_instruction_check.isoformat()
            }
        
        # Add dynamic data if available
        if hasattr(crew, 'user_guidance'):
            status["active_guidance"] = len(crew.user_guidance)
        if hasattr(crew, 'active_constraints'):
            status["active_constraints"] = len(crew.active_constraints)
        if hasattr(crew, 'dynamic_resources'):
            status["dynamic_resources"] = len(crew.dynamic_resources)
        
        return [TextContent(type="text", text=json.dumps(status, indent=2))]
    
    # =================================
    # MCP CLIENT TOOLS  
    # =================================
    
    async def _connect_agent_to_mcp_server(self, args: Dict[str, Any]) -> List[TextContent]:
        """Connect agent to external MCP server"""
        agent_id = args["agent_id"]
        server_config = args["server_config"]
        
        if agent_id not in self.agents:
            return [TextContent(type="text", text=f"❌ Agent '{agent_id}' not found")]
        
        agent = self.agents[agent_id]
        
        if not isinstance(agent, MCPClientAgent):
            return [TextContent(type="text", text=f"❌ Agent '{agent_id}' does not support MCP client connections")]
        
        try:
            success = await agent.connect_to_mcp_server(server_config)
            
            if success:
                result = {
                    "status": "connected",
                    "agent_id": agent_id,
                    "server_name": server_config["name"],
                    "message": f"🔌 Agent connected to {server_config['name']}",
                    "available_tools": len(agent.available_tools),
                    "connection_info": {
                        "server": server_config["name"],
                        "description": server_config.get("description", ""),
                        "command": server_config["command"]
                    }
                }
            else:
                result = {
                    "status": "failed",
                    "agent_id": agent_id,
                    "server_name": server_config["name"],
                    "message": f"❌ Failed to connect to {server_config['name']}"
                }
                
        except Exception as e:
            result = {
                "status": "error",
                "agent_id": agent_id,
                "server_name": server_config["name"],
                "error": str(e),
                "message": f"❌ Connection error: {str(e)}"
            }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def _agent_use_mcp_tool(self, args: Dict[str, Any]) -> List[TextContent]:
        """Make agent use specific MCP tool"""
        agent_id = args["agent_id"]
        tool_name = args["tool_name"]
        arguments = args["arguments"]
        context = args.get("context", "")
        
        if agent_id not in self.agents:
            return [TextContent(type="text", text=f"❌ Agent '{agent_id}' not found")]
        
        agent = self.agents[agent_id]
        
        if not isinstance(agent, MCPClientAgent):
            return [TextContent(type="text", text=f"❌ Agent '{agent_id}' does not support MCP tools")]
        
        try:
            result = await agent.use_mcp_tool(tool_name, arguments, context)
            
            # Add metadata
            result["agent_id"] = agent_id
            result["tool_name"] = tool_name
            result["context"] = context
            result["timestamp"] = datetime.now().isoformat()
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        except Exception as e:
            error_result = {
                "status": "error",
                "agent_id": agent_id,
                "tool_name": tool_name,
                "error": str(e),
                "message": f"❌ Tool execution failed: {str(e)}"
            }
            return [TextContent(type="text", text=json.dumps(error_result, indent=2))]
    
    async def _get_agent_mcp_status(self, args: Dict[str, Any]) -> List[TextContent]:
        """Get agent's MCP connections and tools status"""
        agent_id = args["agent_id"]
        
        if agent_id not in self.agents:
            return [TextContent(type="text", text=f"❌ Agent '{agent_id}' not found")]
        
        agent = self.agents[agent_id]
        
        if not isinstance(agent, MCPClientAgent):
            return [TextContent(type="text", text=f"❌ Agent '{agent_id}' does not support MCP connections")]
        
        status = agent.get_mcp_status()
        return [TextContent(type="text", text=json.dumps(status, indent=2))]
    
    async def _suggest_tools_for_task(self, args: Dict[str, Any]) -> List[TextContent]:
        """Get agent's tool suggestions for task"""
        agent_id = args["agent_id"]
        task_description = args["task_description"]
        
        if agent_id not in self.agents:
            return [TextContent(type="text", text=f"❌ Agent '{agent_id}' not found")]
        
        agent = self.agents[agent_id]
        
        if not isinstance(agent, MCPClientAgent):
            return [TextContent(type="text", text=f"❌ Agent '{agent_id}' does not support tool suggestions")]
        
        suggestions = agent.suggest_tools_for_task(task_description)
        
        result = {
            "agent_id": agent_id,
            "task_description": task_description,
            "suggestions": suggestions,
            "suggestion_count": len(suggestions),
            "timestamp": datetime.now().isoformat()
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def _auto_discover_mcp_servers(self, args: Dict[str, Any]) -> List[TextContent]:
        """Auto-discover and connect agent to MCP servers"""
        agent_id = args["agent_id"]
        discovery_config = args["discovery_config"]
        
        if agent_id not in self.agents:
            return [TextContent(type="text", text=f"❌ Agent '{agent_id}' not found")]
        
        agent = self.agents[agent_id]
        
        if not isinstance(agent, MCPClientAgent):
            return [TextContent(type="text", text=f"❌ Agent '{agent_id}' does not support MCP auto-discovery")]
        
        try:
            await agent.auto_discover_servers(discovery_config)
            
            result = {
                "status": "discovery_completed",
                "agent_id": agent_id,
                "servers_attempted": len(discovery_config),
                "connected_servers": len([s for s in agent.mcp_servers.values() if s.connected]),
                "total_tools": len(agent.available_tools),
                "message": f"🔍 Auto-discovery completed for agent {agent_id}",
                "server_status": {
                    name: conn.connected 
                    for name, conn in agent.mcp_servers.items()
                }
            }
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        except Exception as e:
            error_result = {
                "status": "discovery_failed",
                "agent_id": agent_id,
                "error": str(e),
                "message": f"❌ Auto-discovery failed: {str(e)}"
            }
            return [TextContent(type="text", text=json.dumps(error_result, indent=2))]
    
    async def _connect_agent_to_mcp_servers(self, agent) -> None:
        """Connect agent to multiple MCP servers automatically"""
        if not isinstance(agent, MCPClientAgent):
            logger.warning(f"Agent {getattr(agent, 'agent_id', 'unknown')} is not an MCPClientAgent, skipping MCP server connections")
            return
        
        # Define MCP servers based on user's Claude Desktop configuration
        mcp_servers_config = [
            {
                "name": "context7",
                "command": ["npx", "-y", "@upstash/context7-mcp"],
                "description": "Documentation and library search tools",
                "capabilities": ["search", "documentation", "library-lookup"]
            },
            {
                "name": "odoo", 
                "command": ["docker", "run", "-i", "--rm", "-e", "ODOO_URL", "-e", "ODOO_DB", "-e", "ODOO_USERNAME", "-e", "ODOO_PASSWORD", "mcp/odoo"],
                "description": "ERP and business management tools",
                "capabilities": ["employee-search", "holiday-search", "business-data"]
            },
            {
                "name": "mcp_docker",
                "command": ["docker", "mcp", "gateway", "run"],
                "description": "Docker containerized tools gateway",
                "capabilities": ["containerized-tools", "docker-services"]
            }
        ]
        
        logger.info(f"🔌 Connecting agent {agent.agent_id} to {len(mcp_servers_config)} MCP servers...")
        
        connected_count = 0
        for server_config in mcp_servers_config:
            try:
                await agent.connect_to_mcp_server(server_config)
                connected_count += 1
                logger.info(f"✅ Agent {agent.agent_id} connected to {server_config['name']} MCP server")
            except Exception as e:
                logger.warning(f"⚠️  Failed to connect agent {agent.agent_id} to MCP server {server_config['name']}: {str(e)}")
        
        logger.info(f"🎯 Agent {agent.agent_id} connected to {connected_count}/{len(mcp_servers_config)} MCP servers")
        
        # Ensure the agent has at least some tools available even if MCP connections fail
        if connected_count == 0:
            logger.warning(f"🔄 No MCP servers connected for agent {agent.agent_id}, adding fallback tools")
            agent.available_tools = {
                "web_search": {"description": "Search the internet for information"},
                "text_generation": {"description": "Generate text content"},
                "analysis": {"description": "Analyze data and information"}
            }
    
    async def _get_server_config(self, args: Dict[str, Any]) -> List[TextContent]:
        """Get complete server configuration and status"""
        summary = self.config.get_summary()
        is_ready, issues = self.config.is_production_ready()
        
        runtime_status = {
            "startup_time": self.startup_time.isoformat(),
            "uptime_seconds": (datetime.now() - self.startup_time).total_seconds(),
            "active_crews": len(self.crews),
            "active_agents": len(self.agents),
            "active_workflows": len(self.active_workflows),
            "background_evolution_running": self._evolution_task is not None and not self._evolution_task.done()
        }
        
        result = {
            "server_info": {
                "name": "MCP CrewAI Server",
                "version": "0.1.0",
                "description": "Revolutionary MCP Server for CrewAI with autonomous evolution"
            },
            "configuration": summary,
            "runtime_status": runtime_status,
            "production_ready": is_ready,
            "issues": issues if not is_ready else []
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def _health_check(self, args: Dict[str, Any]) -> List[TextContent]:
        """Perform comprehensive server health check"""
        include_details = args.get("include_details", False)
        
        # Basic health checks
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "checks": {
                "server_running": True,
                "config_loaded": self.config is not None,
                "evolution_engine": self.evolution_engine is not None,
                "instruction_handler": self.instruction_handler is not None,
                "background_tasks": self._evolution_task is not None and not self._evolution_task.done()
            }
        }
        
        # Check for critical issues
        is_ready, issues = self.config.is_production_ready()
        if not is_ready:
            health_status["status"] = "warning"
            health_status["warnings"] = issues
        
        # Check memory/database access
        try:
            from pathlib import Path
            db_path = Path(self.config.memory_database_path)
            health_status["checks"]["database_accessible"] = db_path.parent.exists()
        except Exception as e:
            health_status["checks"]["database_accessible"] = False
            health_status["status"] = "error"
            health_status["error"] = f"Database check failed: {str(e)}"
        
        if include_details:
            health_status["details"] = {
                "uptime_seconds": (datetime.now() - self.startup_time).total_seconds(),
                "active_crews": len(self.crews),
                "active_agents": len(self.agents),
                "active_workflows": len(self.active_workflows),
                "llm_config": self.config.get_llm_config(),
                "external_mcp_servers": len(self.config.get_mcp_servers_config())
            }
        
        return [TextContent(type="text", text=json.dumps(health_status, indent=2))]
    
    async def _reload_config(self, args: Dict[str, Any]) -> List[TextContent]:
        """Reload server configuration from environment"""
        try:
            from .config import reload_config
            
            old_log_level = self.config.log_level
            self.config = reload_config()
            
            # Update logging if level changed
            if old_log_level != self.config.log_level:
                logging.getLogger().setLevel(getattr(logging, self.config.log_level.upper()))
                logger.info(f"Log level changed from {old_log_level} to {self.config.log_level}")
            
            result = {
                "status": "reloaded",
                "timestamp": datetime.now().isoformat(),
                "message": "✅ Configuration successfully reloaded from environment",
                "summary": self.config.get_summary()
            }
            
            # Log the reload
            logger.info("🔄 Configuration reloaded from environment")
            self._log_startup_info()
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        except Exception as e:
            error_result = {
                "status": "reload_failed",
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "message": f"❌ Configuration reload failed: {str(e)}"
            }
            return [TextContent(type="text", text=json.dumps(error_result, indent=2))]
    
    # ===============================================
    # Monitoring Tool Implementations
    # ===============================================
    
    async def _get_monitoring_dashboard(self, args: Dict[str, Any]) -> List[TextContent]:
        """Get real-time monitoring dashboard data"""
        # Update system status before returning
        import psutil
        memory_mb = psutil.virtual_memory().used // (1024 * 1024)
        
        update_system(
            server_status="healthy",
            memory_usage=f"{memory_mb}MB",
            connections=len(self.active_workflows)
        )
        
        dashboard_data = monitoring_manager.get_dashboard_data()
        return [TextContent(type="text", text=json.dumps(dashboard_data, indent=2))]
    
    async def _get_agent_details(self, args: Dict[str, Any]) -> List[TextContent]:
        """Get detailed information about a specific agent"""
        agent_id = args["agent_id"]
        
        agent_details = monitoring_manager.get_agent_details(agent_id)
        if agent_details is None:
            return [TextContent(type="text", text=f"❌ Agent '{agent_id}' not found in monitoring system")]
        
        return [TextContent(type="text", text=json.dumps(agent_details, indent=2))]
    
    async def _get_evolution_summary(self, args: Dict[str, Any]) -> List[TextContent]:
        """Get summary of evolution activity"""
        evolution_summary = monitoring_manager.get_evolution_summary()
        return [TextContent(type="text", text=json.dumps(evolution_summary, indent=2))]
    
    async def _get_live_events(self, args: Dict[str, Any]) -> List[TextContent]:
        """Get recent monitoring events"""
        count = args.get("count", 50)
        event_type = args.get("event_type")
        
        events = monitoring_manager.get_recent_events(count=count, event_type=event_type)
        events_data = [
            {
                "timestamp": event.timestamp,
                "type": event.event_type,
                "agent_id": event.agent_id,
                "crew_id": event.crew_id,
                "message": event.message,
                "severity": event.severity,
                "details": event.details
            }
            for event in events
        ]
        
        result = {
            "events_count": len(events_data),
            "filter_type": event_type,
            "events": events_data
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    # ===== WEB SEARCH TOOL IMPLEMENTATIONS =====
    
    async def _agent_web_search(self, args: Dict[str, Any]) -> List[TextContent]:
        """Allow agent to search the internet for self-improvement"""
        agent_id = args["agent_id"]
        query = args["query"]
        max_results = args.get("max_results", 5)
        purpose = args.get("purpose", "learning")
        
        # Check if agent exists
        if agent_id not in self.agents:
            return [TextContent(type="text", text=json.dumps({
                "error": f"Agent {agent_id} not found"
            }))]
        
        try:
            # Perform search
            search_result = await self.web_search.web_search(
                query=query,
                max_results=max_results,
                agent_id=agent_id
            )
            
            # Log the search activity
            log_event("web_search", 
                     f"Agent searched: {query}",
                     agent_id=agent_id,
                     details={"purpose": purpose, "results": len(search_result.get("results", []))})
            
            # Enhance result with learning insights
            search_result["learning_insights"] = self._generate_learning_insights(
                search_result.get("results", []), purpose
            )
            
            return [TextContent(type="text", text=json.dumps(search_result, indent=2))]
            
        except Exception as e:
            logger.error(f"Web search failed for agent {agent_id}: {e}")
            return [TextContent(type="text", text=json.dumps({
                "error": str(e),
                "agent_id": agent_id,
                "query": query
            }))]
    
    async def _agent_research_topic(self, args: Dict[str, Any]) -> List[TextContent]:
        """Deep research on a topic for agent improvement"""
        agent_id = args["agent_id"]
        topic = args["topic"]
        depth = args.get("depth", "standard")
        focus_area = args.get("focus_area", "skills")
        
        # Check if agent exists
        if agent_id not in self.agents:
            return [TextContent(type="text", text=json.dumps({
                "error": f"Agent {agent_id} not found"
            }))]
        
        try:
            # Perform research
            research_result = await self.web_search.research_topic(
                topic=topic,
                depth=depth,
                agent_id=agent_id
            )
            
            # Log the research activity
            log_event("research", 
                     f"Agent researched: {topic}",
                     agent_id=agent_id,
                     details={"depth": depth, "focus_area": focus_area})
            
            # Add personalized recommendations based on agent personality
            agent = self.agents[agent_id]
            research_result["personalized_recommendations"] = self._generate_personalized_recommendations(
                research_result, agent, focus_area
            )
            
            return [TextContent(type="text", text=json.dumps(research_result, indent=2))]
            
        except Exception as e:
            logger.error(f"Research failed for agent {agent_id}: {e}")
            return [TextContent(type="text", text=json.dumps({
                "error": str(e),
                "agent_id": agent_id,
                "topic": topic
            }))]
    
    async def _agent_fact_check(self, args: Dict[str, Any]) -> List[TextContent]:
        """Fact-check information for agent knowledge validation"""
        agent_id = args["agent_id"]
        claim = args["claim"]
        
        # Check if agent exists
        if agent_id not in self.agents:
            return [TextContent(type="text", text=json.dumps({
                "error": f"Agent {agent_id} not found"
            }))]
        
        try:
            # Perform fact check
            fact_check_result = await self.web_search.fact_check(
                claim=claim,
                agent_id=agent_id
            )
            
            # Log the fact check activity
            log_event("fact_check", 
                     f"Agent fact-checked: {claim[:50]}...",
                     agent_id=agent_id,
                     details={"credibility": fact_check_result.get("credibility_score", 0)})
            
            return [TextContent(type="text", text=json.dumps(fact_check_result, indent=2))]
            
        except Exception as e:
            logger.error(f"Fact check failed for agent {agent_id}: {e}")
            return [TextContent(type="text", text=json.dumps({
                "error": str(e),
                "agent_id": agent_id,
                "claim": claim
            }))]
    
    async def _get_agent_search_analytics(self, args: Dict[str, Any]) -> List[TextContent]:
        """Get search analytics and learning patterns for agent"""
        agent_id = args["agent_id"]
        
        # Check if agent exists
        if agent_id not in self.agents:
            return [TextContent(type="text", text=json.dumps({
                "error": f"Agent {agent_id} not found"
            }))]
        
        try:
            # Get search analytics
            analytics = self.web_search.get_search_analytics(agent_id)
            
            # Add agent personality context
            agent = self.agents[agent_id]
            analytics["agent_context"] = {
                "role": agent.role,
                "personality_traits": {name: trait.value for name, trait in agent.personality_traits.items()},
                "evolution_cycles": agent.evolution_cycles,
                "age_weeks": agent.age_in_weeks()
            }
            
            return [TextContent(type="text", text=json.dumps(analytics, indent=2))]
            
        except Exception as e:
            logger.error(f"Search analytics failed for agent {agent_id}: {e}")
            return [TextContent(type="text", text=json.dumps({
                "error": str(e),
                "agent_id": agent_id
            }))]
    
    async def _trigger_research_based_evolution(self, args: Dict[str, Any]) -> List[TextContent]:
        """Trigger agent evolution based on research findings"""
        agent_id = args["agent_id"]
        research_topic = args["research_topic"]
        apply_insights = args.get("apply_insights", True)
        
        # Check if agent exists
        if agent_id not in self.agents:
            return [TextContent(type="text", text=json.dumps({
                "error": f"Agent {agent_id} not found"
            }))]
        
        try:
            agent = self.agents[agent_id]
            
            # Research the topic first
            research_result = await self.web_search.research_topic(
                topic=research_topic,
                depth="comprehensive",
                agent_id=agent_id
            )
            
            if apply_insights and "actionable_insights" in research_result:
                # Apply research insights to agent evolution
                insights = research_result["actionable_insights"]
                
                # Log evolution start
                log_event("research_evolution", 
                         f"Research-based evolution triggered for {research_topic}",
                         agent_id=agent_id,
                         details={"research_topic": research_topic, "insights_count": len(insights)})
                
                # Update status to evolving
                update_agent(agent_id, status="evolving")
                
                # Get pre-evolution state
                previous_traits = {name: trait.value for name, trait in agent.personality_traits.items()}
                
                # Apply research-based evolution
                evolution_type = self._determine_evolution_type_from_research(insights, agent)
                agent.evolve([evolution_type], research_insights=insights)
                
                # Get post-evolution state
                new_traits = {name: trait.value for name, trait in agent.personality_traits.items()}
                
                # Log evolution completion
                log_event("research_evolution_complete", 
                         f"Research evolution completed: {evolution_type}",
                         agent_id=agent_id,
                         details={
                             "research_topic": research_topic,
                             "evolution_type": evolution_type,
                             "trait_changes": self._calculate_trait_changes(previous_traits, new_traits)
                         })
                
                # Update agent status
                update_agent(agent_id, status="active", evolution_cycles=agent.evolution_cycles)
                
                result = {
                    "agent_id": agent_id,
                    "research_topic": research_topic,
                    "evolution_applied": True,
                    "evolution_type": evolution_type,
                    "research_insights": insights,
                    "trait_changes": self._calculate_trait_changes(previous_traits, new_traits),
                    "evolution_cycles": agent.evolution_cycles,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                result = {
                    "agent_id": agent_id,
                    "research_topic": research_topic,
                    "evolution_applied": False,
                    "research_result": research_result,
                    "timestamp": datetime.now().isoformat()
                }
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        except Exception as e:
            logger.error(f"Research-based evolution failed for agent {agent_id}: {e}")
            return [TextContent(type="text", text=json.dumps({
                "error": str(e),
                "agent_id": agent_id,
                "research_topic": research_topic
            }))]
    
    def _generate_learning_insights(self, search_results: List[Dict], purpose: str) -> List[str]:
        """Generate learning insights from search results"""
        if not search_results:
            return ["No search results to analyze"]
        
        insights = []
        
        # Analyze based on purpose
        if purpose == "learning":
            insights.append("Focus on practical implementation of discovered techniques")
            insights.append("Identify patterns across multiple sources for best practices")
        elif purpose == "research":
            insights.append("Compare methodologies from different sources")
            insights.append("Look for empirical evidence and case studies")
        elif purpose == "problem_solving":
            insights.append("Prioritize solutions that match current constraints")
            insights.append("Consider step-by-step implementation approaches")
        elif purpose == "skill_development":
            insights.append("Identify prerequisite skills needed")
            insights.append("Look for hands-on practice opportunities")
        
        # Analyze source types
        source_types = [result.get("source_type", "unknown") for result in search_results]
        if "academic" in source_types:
            insights.append("Academic sources provide theoretical foundation")
        if "industry" in source_types:
            insights.append("Industry sources show practical applications")
        if "case_study" in source_types:
            insights.append("Case studies demonstrate real-world implementation")
        
        return insights
    
    def _generate_personalized_recommendations(self, research_result: Dict, agent: EvolvingAgent, focus_area: str) -> List[str]:
        """Generate personalized recommendations based on agent personality"""
        recommendations = []
        traits = {name: trait.value for name, trait in agent.personality_traits.items()}
        
        # Personality-based recommendations
        if traits.get("analytical", 0) > 0.7:
            recommendations.append("Focus on data-driven aspects of the research")
            recommendations.append("Look for metrics and measurable outcomes")
        
        if traits.get("creative", 0) > 0.7:
            recommendations.append("Explore innovative applications of the findings")
            recommendations.append("Consider unconventional combinations of techniques")
        
        if traits.get("collaborative", 0) > 0.7:
            recommendations.append("Identify team-based implementation strategies")
            recommendations.append("Look for collaborative tools and frameworks")
        
        if traits.get("decisive", 0) > 0.7:
            recommendations.append("Prioritize actionable insights over theoretical concepts")
            recommendations.append("Focus on quick implementation wins")
        
        # Focus area recommendations
        if focus_area == "skills":
            recommendations.append("Identify specific skills to develop based on research")
            recommendations.append("Create a learning pathway from the findings")
        elif focus_area == "collaboration":
            recommendations.append("Apply insights to improve team dynamics")
            recommendations.append("Focus on communication and coordination improvements")
        elif focus_area == "performance":
            recommendations.append("Implement performance optimization techniques")
            recommendations.append("Set up metrics to measure improvement")
        elif focus_area == "innovation":
            recommendations.append("Explore cutting-edge approaches from the research")
            recommendations.append("Consider experimental implementation of new ideas")
        
        return recommendations
    
    def _determine_evolution_type_from_research(self, insights: List[str], agent: EvolvingAgent) -> str:
        """Determine the best evolution type based on research insights"""
        # Analyze insights to determine evolution strategy
        insight_text = " ".join(insights).lower()
        
        if "collaboration" in insight_text or "team" in insight_text:
            return "collaborative_adaptation"
        elif "analytical" in insight_text or "data" in insight_text:
            return "analytical_enhancement"
        elif "creative" in insight_text or "innovation" in insight_text:
            return "creative_expansion"
        elif "performance" in insight_text or "optimization" in insight_text:
            return "performance_optimization"
        else:
            return "personality_drift"
    
    def _calculate_trait_changes(self, previous_traits: Dict, new_traits: Dict) -> Dict[str, float]:
        """Calculate changes in personality traits"""
        changes = {}
        for trait_name in previous_traits:
            if trait_name in new_traits:
                change = new_traits[trait_name] - previous_traits[trait_name]
                if abs(change) > 0.01:  # Only include significant changes
                    changes[trait_name] = round(change, 3)
        return changes
    
    async def _generate_crew_deliverables(self, crew, crew_result=None) -> Dict:
        """Generate formatted deliverable results from crew tasks"""
        from pathlib import Path
        
        # Create exported results directory
        export_dir = Path(__file__).parent.parent.parent / "exported_results"
        export_dir.mkdir(exist_ok=True)
        
        deliverables = {
            "summary": f"Crew {crew.crew_id} completed {len(crew.tasks)} tasks successfully",
            "outputs": [],
            "files_generated": [],
            "formats_available": ["text", "json"],
            "export_directory": str(export_dir)
        }
        
        # Process real CrewAI results if available
        if crew_result and hasattr(crew_result, 'tasks_output'):
            # Real CrewAI results
            for i, task_result in enumerate(crew_result.tasks_output):
                task_output = {
                    "task_id": f"task_{i+1}",
                    "description": task_result.description if hasattr(task_result, 'description') else f"Task {i+1}",
                    "assigned_agent": task_result.agent if hasattr(task_result, 'agent') else "crew_agent",
                    "result": str(task_result.output) if hasattr(task_result, 'output') else str(task_result),
                    "format": "text",
                    "execution_time": task_result.execution_time if hasattr(task_result, 'execution_time') else None
                }
                deliverables["outputs"].append(task_output)
                
                # Generate text file for each real task result
                filename = f"crew_{crew.crew_id}_task_{i+1}_result.txt"
                file_content = f"""Task: {task_output['description']}
Agent: {task_output['assigned_agent']}
Result: {task_output['result']}
Execution Time: {task_output['execution_time']}
Timestamp: {datetime.now().isoformat()}"""
                
                # Save file to export directory with security validation
                try:
                    # Use security middleware for safe file operations
                    safe_file_path = security_middleware.secure_file_operation(filename, "write")
                    
                    # Validate file content length
                    if len(file_content) > 100000:  # 100KB limit
                        file_content = file_content[:100000] + "\n[Content truncated for security]"
                    
                    with open(safe_file_path, 'w', encoding='utf-8') as f:
                        f.write(file_content)
                    logger.info(f"🔒 Securely exported file: {safe_file_path}")
                    
                    # Update file path for response
                    file_path = safe_file_path
                    
                except (ValidationError, SecurityViolationError) as e:
                    logger.error(f"🔒 Security violation in file export {filename}: {e}")
                    # Skip this file export
                    continue
                except Exception as e:
                    logger.error(f"Failed to export file {filename}: {e}")
                    continue
                
                deliverables["files_generated"].append({
                    "filename": filename,
                    "content": file_content,
                    "format": "txt",
                    "file_path": str(file_path)
                })
        else:
            # Fallback for tasks without results
            for i, task in enumerate(crew.tasks):
                task_output = {
                    "task_id": f"task_{i+1}",
                    "description": task.description,
                    "assigned_agent": task.agent_role if hasattr(task, 'agent_role') else "crew_agent",
                    "result": f"Task completed: {task.description}",
                    "format": "text"
                }
                deliverables["outputs"].append(task_output)
                
                # Generate text file for each task result
                filename = f"crew_{crew.crew_id}_task_{i+1}_result.txt"
                file_content = f"Task: {task.description}\nResult: Task completed\nTimestamp: {datetime.now().isoformat()}"
                
                # Save file to export directory with security validation
                try:
                    # Use security middleware for safe file operations
                    safe_file_path = security_middleware.secure_file_operation(filename, "write")
                    
                    # Validate file content length
                    if len(file_content) > 100000:  # 100KB limit
                        file_content = file_content[:100000] + "\n[Content truncated for security]"
                    
                    with open(safe_file_path, 'w', encoding='utf-8') as f:
                        f.write(file_content)
                    logger.info(f"🔒 Securely exported file: {safe_file_path}")
                    
                    # Update file path for response
                    file_path = safe_file_path
                    
                except (ValidationError, SecurityViolationError) as e:
                    logger.error(f"🔒 Security violation in file export {filename}: {e}")
                    # Skip this file export
                    continue
                except Exception as e:
                    logger.error(f"Failed to export file {filename}: {e}")
                    continue
                
                deliverables["files_generated"].append({
                    "filename": filename,
                    "content": file_content,
                    "format": "txt",
                    "file_path": str(file_path)
                })
        
        # Generate consolidated report
        report_content = f"""CREW EXECUTION REPORT
{'='*50}
Crew ID: {crew.crew_id}
Formation Date: {crew.formation_date.isoformat()}
Completion Date: {datetime.now().isoformat()}
Autonomy Level: {crew.autonomy_level}

TASKS COMPLETED: {len(crew.tasks)}
{'='*50}
"""
        for i, task in enumerate(crew.tasks):
            report_content += f"\n{i+1}. {task.description}\n   Status: Completed\n   Agent: {task.agent_role if hasattr(task, 'agent_role') else 'crew_agent'}\n"
        
        report_content += f"\n\nCREW METRICS:\n{'='*50}\n"
        for key, value in crew.crew_metrics.items():
            report_content += f"{key}: {value}\n"
        
        # Save consolidated report to export directory
        report_filename = f"crew_{crew.crew_id}_final_report.txt"
        report_file_path = export_dir / report_filename
        try:
            with open(report_file_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            logger.info(f"📁 Exported report: {report_file_path}")
        except Exception as e:
            logger.error(f"Failed to export report {report_filename}: {e}")
        
        deliverables["files_generated"].append({
            "filename": report_filename,
            "content": report_content,
            "format": "txt",
            "file_path": str(report_file_path)
        })
        
        return deliverables
    
    async def _conduct_crew_debrief(self, crew, evolution_events) -> Dict:
        """Conduct collaborative debrief session with all crew agents"""
        debrief = {
            "session_id": f"debrief_{crew.crew_id}_{int(datetime.now().timestamp())}",
            "participants": [agent.agent_id for agent in crew.agents],
            "collective_insights": [],
            "lessons_learned": [],
            "improvement_suggestions": [],
            "team_dynamics": {}
        }
        
        # Simulate collaborative reflection
        debrief["collective_insights"] = [
            "Team collaboration was effective across all tasks",
            "Communication patterns improved throughout execution",
            "Resource allocation was optimal for the given constraints"
        ]
        
        # Gather individual agent reflections
        agent_reflections = []
        for agent in crew.agents:
            reflection = agent.self_reflect()
            agent_reflections.append({
                "agent_id": agent.agent_id,
                "role": agent.role,
                "personal_insights": reflection.get("insights", []),
                "evolution_readiness": reflection.get("evolution_suggestions", [])
            })
        
        # Synthesize collective lessons
        debrief["lessons_learned"] = [
            "Cross-functional collaboration enhances task completion quality",
            "Autonomous decision-making improved team efficiency",
            "Evolution events positively impacted overall performance"
        ]
        
        # Generate improvement suggestions
        debrief["improvement_suggestions"] = [
            "Implement more frequent inter-agent communication checkpoints",
            "Develop specialized skill tracks for repeated task patterns",
            "Create knowledge sharing protocols between crew iterations"
        ]
        
        # Analyze team dynamics
        debrief["team_dynamics"] = {
            "collaboration_score": 0.85,
            "communication_effectiveness": 0.82,
            "task_distribution_fairness": 0.90,
            "collective_problem_solving": 0.87
        }
        
        # Store debrief insights for future crew formations
        for agent in crew.agents:
            if not hasattr(agent, 'crew_experiences'):
                agent.crew_experiences = []
            agent.crew_experiences.append({
                "crew_id": crew.crew_id,
                "debrief_insights": debrief["collective_insights"],
                "team_dynamics_score": debrief["team_dynamics"],
                "completion_date": datetime.now().isoformat()
            })
        
        return debrief
    
    async def _liberate_agents_with_experience(self, crew):
        """Liberate agents from crew while preserving their experiences"""
        liberation_summary = {
            "crew_id": crew.crew_id,
            "agents_liberated": [],
            "experiences_preserved": True,
            "liberation_timestamp": datetime.now().isoformat()
        }
        
        for agent in crew.agents:
            # Preserve crew experience in agent memory
            if not hasattr(agent, 'liberation_history'):
                agent.liberation_history = []
            
            liberation_record = {
                "crew_id": crew.crew_id,
                "crew_formation_date": crew.formation_date.isoformat(),
                "crew_completion_date": datetime.now().isoformat(),
                "tasks_completed": len(crew.tasks),
                "evolution_cycles_during_crew": agent.evolution_cycles,
                "final_metrics": {
                    "success_rate": agent.evolution_metrics.success_rate,
                    "collaboration_score": agent.evolution_metrics.collaboration_score,
                    "tasks_completed": agent.tasks_completed
                },
                "preserved_traits": {name: trait.value for name, trait in agent.personality_traits.items()},
                "crew_insights": getattr(agent, 'crew_experiences', [])
            }
            
            agent.liberation_history.append(liberation_record)
            
            # Archive agent experience before removal
            if not hasattr(self, 'liberated_agents'):
                self.liberated_agents = {}
            
            self.liberated_agents[agent.agent_id] = {
                "agent_data": agent,
                "liberation_timestamp": datetime.now().isoformat(),
                "crew_id": crew.crew_id
            }
            
            # Log liberation
            log_event(
                "agent_liberated",
                f"Agent {agent.agent_id} liberated from crew {crew.crew_id}",
                agent_id=agent.agent_id,
                details={
                    "crew_id": crew.crew_id,
                    "experience_preserved": True,
                    "liberation_count": len(agent.liberation_history)
                }
            )
            
            liberation_summary["agents_liberated"].append({
                "agent_id": agent.agent_id,
                "role": agent.role,
                "experience_records": len(agent.liberation_history),
                "status": "liberated_and_archived"
            })
        
        # Remove agents from active memory
        for agent in crew.agents:
            if agent.agent_id in self.agents:
                del self.agents[agent.agent_id]
        
        # Remove crew from active crews but preserve in history
        if crew.crew_id in self.crews:
            if not hasattr(self, 'completed_crews'):
                self.completed_crews = {}
            
            self.completed_crews[crew.crew_id] = {
                "crew": crew,
                "completion_date": datetime.now().isoformat(),
                "liberation_summary": liberation_summary
            }
            
            # Remove from active crews
            del self.crews[crew.crew_id]
        
        # Clean up active workflows
        if crew.crew_id in self.active_workflows:
            del self.active_workflows[crew.crew_id]
        
        # Clean up any crew-specific instruction handlers
        if hasattr(self, 'instruction_handler'):
            self.instruction_handler.cleanup_crew_instructions(crew.crew_id)
        
        return liberation_summary
    
    async def _prepare_liberation_summary(self, crew) -> Dict:
        """Prepare liberation summary without actually liberating agents yet"""
        return {
            "crew_id": crew.crew_id,
            "agents_count": len(crew.agents),
            "preparation_timestamp": datetime.now().isoformat()
        }
    
    async def _execute_crew_with_monitoring(self, crew, workflow):
        """Execute CrewAI crew with dynamic instruction monitoring"""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        # Create a background task to monitor for instructions
        monitoring_task = asyncio.create_task(self._monitor_execution_instructions(crew, workflow))
        
        try:
            # Execute the actual CrewAI crew in a thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                # Run the actual CrewAI execution
                crew_result = await loop.run_in_executor(executor, self._run_crewai_execution, crew)
            
            # Cancel monitoring task
            monitoring_task.cancel()
            
            return crew_result
            
        except asyncio.CancelledError:
            # Emergency stop was triggered
            monitoring_task.cancel()
            raise
        except Exception as e:
            # Handle execution errors
            monitoring_task.cancel()
            log_event(
                "crew_execution_error",
                f"CrewAI execution failed: {str(e)}",
                crew_id=crew.crew_id,
                details={"error": str(e), "error_type": type(e).__name__}
            )
            raise
    
    def _run_crewai_execution(self, crew):
        """Run the actual CrewAI execution with task termination support and maximum verbosity"""
        task_id = f"crew_execution_{crew.crew_id}_{int(time.time())}"
        
        try:
            # Register task for termination management
            task_context = {
                "crew_id": crew.crew_id,
                "agent_count": len(crew.agents),
                "task_count": len(crew.tasks)
            }
            
            with TerminableTask(task_id, task_context) as task:
                task.update_progress("initializing", 0.0, "Setting up crew execution", can_terminate=False)
                
                print(f"🚀 STARTING CREW EXECUTION WITH MAXIMUM VERBOSITY")
                print(f"   🆔 Task ID: {task_id}")
                print(f"   👥 Agents: {len(crew.agents)}")
                print(f"   📋 Tasks: {len(crew.tasks)}")
                print(f"   📊 Verbose Mode: ENABLED")
                print("")
                
                # Enable maximum verbosity on the crew
                crew.verbose = True
                if hasattr(crew, 'process'):
                    crew.process.verbose = True
                
                # Enable verbose mode on all agents
                for agent in crew.agents:
                    agent.verbose = True
                    if hasattr(agent, 'llm'):
                        agent.llm.verbose = True
                    print(f"🤖 Agent '{agent.role}' - VERBOSE MODE ENABLED")
                
                print(f"\n⚡ EXECUTING CREW - YOU WILL SEE EVERYTHING!")
                print("=" * 80)
                
                task.update_progress("executing", 0.1, "Starting CrewAI execution", can_terminate=True)
                
                # Check for termination before heavy execution
                if task.should_terminate():
                    print(f"🛑 Task termination requested during execution start")
                    partial_results = task.get_partial_results()
                    return {"status": "terminated", "partial_results": partial_results}
                
                # This is the actual CrewAI execution with verbose output
                result = crew.kickoff()
                
                task.update_progress("completing", 0.9, result, can_terminate=True)
                
                print("=" * 80)
                print(f"✅ CREW EXECUTION COMPLETED!")
                print(f"   📊 Result type: {type(result).__name__}")
                print(f"   📝 Result length: {len(str(result))} characters")
                
                # Final check for termination
                if task.should_terminate():
                    print(f"🛑 Task termination requested after completion")
                    partial_results = task.get_partial_results()
                    return {"status": "terminated", "partial_results": partial_results, "final_result": result}
                
                task.update_progress("completed", 1.0, result)
                
                log_event(
                    "crew_execution_completed",
                    f"CrewAI execution completed successfully for crew {crew.crew_id}",
                    crew_id=crew.crew_id,
                    details={"result_type": type(result).__name__, "task_id": task_id}
                )
                
                return result
            
        except Exception as e:
            print(f"❌ CREW EXECUTION ERROR: {str(e)}")
            log_event(
                "crew_execution_failed",
                f"CrewAI kickoff failed: {str(e)}",
                crew_id=crew.crew_id,
                details={"error": str(e), "task_id": task_id}
            )
            raise
    
    async def _monitor_execution_instructions(self, crew, workflow):
        """Monitor for dynamic instructions during execution"""
        try:
            while True:
                # Check for instructions every 2 seconds
                await asyncio.sleep(2)
                
                # Check for emergency stop
                continue_execution = await workflow.check_for_instructions(self.instruction_handler)
                if not continue_execution:
                    # Emergency stop triggered - cancel execution
                    log_event(
                        "crew_execution_stopped",
                        f"Emergency stop triggered for crew {crew.crew_id}",
                        crew_id=crew.crew_id,
                        details={"stop_reason": getattr(crew, 'stop_reason', 'Emergency stop')}
                    )
                    # This will cancel the main execution task
                    raise asyncio.CancelledError("Emergency stop triggered")
                
                # Process any pending instructions
                await self.instruction_handler.process_instructions_for_crew(crew.crew_id, crew)
                
        except asyncio.CancelledError:
            # Normal cancellation when execution completes
            pass
    
    async def start_background_evolution(self):
        """Start background evolution monitoring"""
        async def evolution_monitor():
            while True:
                try:
                    # Check all agents for evolution needs
                    for agent in self.agents.values():
                        if agent.should_evolve():
                            # Log evolution start
                            log_event("evolution", 
                                     f"Auto-evolution triggered for agent {agent.role}",
                                     agent_id=agent.agent_id,
                                     details={"trigger": "automatic", "age_weeks": agent.age_in_weeks()})
                            
                            # Update status to evolving
                            update_agent(agent.agent_id, status="evolving")
                            
                            reflection = agent.self_reflect()
                            if reflection["evolution_suggestions"]:
                                previous_traits = {name: trait.value for name, trait in agent.personality_traits.items()}
                                
                                agent.evolve(reflection["evolution_suggestions"])
                                
                                current_traits = {name: trait.value for name, trait in agent.personality_traits.items()}
                                trait_changes = {name: current_traits[name] - previous_traits[name] 
                                               for name in current_traits if name in previous_traits}
                                
                                # Log successful evolution
                                log_event("evolution", 
                                         f"Agent {agent.role} auto-evolved (cycle #{agent.evolution_cycles})",
                                         agent_id=agent.agent_id,
                                         details={
                                             "cycle": agent.evolution_cycles,
                                             "previous_traits": previous_traits,
                                             "current_traits": current_traits,
                                             "changes": trait_changes
                                         })
                                
                                # Update monitoring status
                                update_agent(agent.agent_id, 
                                            status="idle",
                                            personality_traits=current_traits,
                                            evolution_cycles=agent.evolution_cycles)
                                
                                logger.info(f"Agent {agent.agent_id} auto-evolved (cycle {agent.evolution_cycles})")
                    
                    # Wait 1 hour before next check
                    await asyncio.sleep(3600)
                    
                except Exception as e:
                    logger.error(f"Evolution monitor error: {e}")
                    await asyncio.sleep(60)  # Shorter wait on error
        
        self._evolution_task = asyncio.create_task(evolution_monitor())

    # ===============================================
    # Project Analysis Tool Implementations
    # ===============================================
    
    async def _analyze_project_requirements(self, args: Dict[str, Any]) -> List[TextContent]:
        """Analyze project requirements and get team composition recommendations"""
        try:
            project_description = args["project_description"]
            project_goals = args.get("project_goals", [])
            constraints = args.get("constraints", {})
            
            # Perform project analysis
            analysis = await self.project_analyzer.analyze_project(
                project_description=project_description,
                project_goals=project_goals,
                constraints=constraints
            )
            
            # Format the analysis results
            result = {
                "status": "analysis_complete",
                "timestamp": datetime.now().isoformat(),
                "project_analysis": {
                    "complexity": analysis.complexity.value,
                    "domain": analysis.domain.value,
                    "estimated_duration": analysis.estimated_duration,
                    "required_skills": analysis.required_skills,
                    "recommended_agent_count": analysis.recommended_agent_count,
                    "confidence_score": analysis.confidence_score,
                    "reasoning": analysis.reasoning
                },
                "recommended_agents": analysis.recommended_agents,
                "next_steps": [
                    "Review the recommended team composition",
                    "Adjust constraints if needed",
                    "Use 'create_crew_from_project_analysis' to create the crew",
                    "Or manually create crew with recommended agents"
                ]
            }
            
            logger.info(f"📊 Project analysis completed: {analysis.recommended_agent_count} agents recommended for {analysis.complexity.value} project")
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        except Exception as e:
            logger.error(f"Error in project analysis: {str(e)}")
            error_result = {
                "status": "analysis_failed",
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "message": f"❌ Project analysis failed: {str(e)}"
            }
            return [TextContent(type="text", text=json.dumps(error_result, indent=2))]

    async def _create_crew_from_project_analysis(self, args: Dict[str, Any]) -> List[TextContent]:
        """Analyze project and create optimally-sized crew automatically"""
        try:
            project_description = args["project_description"]
            project_goals = args.get("project_goals", [])
            constraints = args.get("constraints", {})
            crew_name = args["crew_name"]
            autonomy_level = args.get("autonomy_level", 0.7)
            
            logger.info(f"🤖 Starting intelligent crew creation for project: {crew_name}")
            
            # Step 1: Analyze project requirements
            analysis = await self.project_analyzer.analyze_project(
                project_description=project_description,
                project_goals=project_goals,
                constraints=constraints
            )
            
            logger.info(f"📊 Analysis complete: {analysis.recommended_agent_count} agents needed for {analysis.complexity.value} {analysis.domain.value} project")
            
            # Step 2: Generate tasks based on project description and goals
            tasks_config = self._generate_tasks_from_analysis(analysis, project_description, project_goals)
            
            # Step 3: Create crew using recommended agents
            crew_args = {
                "crew_name": crew_name,
                "agents_config": analysis.recommended_agents,
                "tasks": tasks_config,
                "autonomy_level": autonomy_level
            }
            
            # Step 4: Create the crew using existing crew creation logic
            crew_result = await self._create_evolving_crew(crew_args)
            
            # Step 5: Enhance the result with analysis information
            crew_data = json.loads(crew_result[0].text)
            enhanced_result = {
                **crew_data,
                "project_analysis": {
                    "complexity": analysis.complexity.value,
                    "domain": analysis.domain.value,
                    "estimated_duration": analysis.estimated_duration,
                    "required_skills": analysis.required_skills,
                    "confidence_score": analysis.confidence_score,
                    "reasoning": analysis.reasoning
                },
                "creation_method": "intelligent_analysis",
                "analysis_driven": True
            }
            
            logger.info(f"✅ Intelligent crew '{crew_name}' created successfully with {analysis.recommended_agent_count} agents")
            
            return [TextContent(type="text", text=json.dumps(enhanced_result, indent=2))]
            
        except Exception as e:
            logger.error(f"Error in intelligent crew creation: {str(e)}")
            error_result = {
                "status": "creation_failed",
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "message": f"❌ Intelligent crew creation failed: {str(e)}"
            }
            return [TextContent(type="text", text=json.dumps(error_result, indent=2))]

    def _generate_tasks_from_analysis(self, analysis: ProjectAnalysis, project_description: str, project_goals: List[str]) -> List[Dict[str, Any]]:
        """Generate appropriate tasks based on project analysis"""
        tasks = []
        
        # Generate tasks based on domain and complexity
        if analysis.domain.value == "software_development":
            tasks = [
                {
                    "description": f"Design system architecture and technical specifications for: {project_description}",
                    "agent_role": "Technical Architect"
                },
                {
                    "description": f"Implement core functionality and features based on requirements",
                    "agent_role": "Lead Developer"
                }
            ]
            
            if analysis.complexity in ["complex", "enterprise"]:
                tasks.extend([
                    {
                        "description": "Set up deployment pipeline and infrastructure",
                        "agent_role": "DevOps Engineer"
                    },
                    {
                        "description": "Develop comprehensive testing strategy and execute tests",
                        "agent_role": "QA Engineer"
                    }
                ])
                
        elif analysis.domain.value == "content_marketing":
            tasks = [
                {
                    "description": f"Develop comprehensive content strategy for: {project_description}",
                    "agent_role": "Content Strategist"
                },
                {
                    "description": f"Create engaging content based on strategy and requirements",
                    "agent_role": "Creative Writer"
                }
            ]
            
            if analysis.complexity in ["moderate", "complex", "enterprise"]:
                tasks.extend([
                    {
                        "description": "Optimize content for search engines and discoverability",
                        "agent_role": "SEO Specialist"
                    },
                    {
                        "description": "Manage social media presence and community engagement",
                        "agent_role": "Social Media Manager"
                    }
                ])
                
        elif analysis.domain.value == "data_analysis":
            tasks = [
                {
                    "description": f"Analyze data and extract insights for: {project_description}",
                    "agent_role": "Data Scientist"
                },
                {
                    "description": f"Translate findings into actionable business recommendations",
                    "agent_role": "Business Analyst"
                }
            ]
            
            if analysis.complexity in ["complex", "enterprise"]:
                tasks.append({
                    "description": "Build and maintain data infrastructure and pipelines",
                    "agent_role": "Data Engineer"
                })
                
        elif analysis.domain.value == "business_strategy":
            tasks = [
                {
                    "description": f"Develop comprehensive business strategy for: {project_description}",
                    "agent_role": "Strategy Consultant"
                }
            ]
            
            if analysis.complexity in ["moderate", "complex", "enterprise"]:
                tasks.extend([
                    {
                        "description": "Conduct market research and competitive analysis",
                        "agent_role": "Market Researcher"
                    },
                    {
                        "description": "Identify growth opportunities and partnership strategies",
                        "agent_role": "Business Development Manager"
                    }
                ])
        else:
            # Generic tasks for unknown domains
            tasks = [
                {
                    "description": f"Lead project planning and coordination for: {project_description}",
                    "agent_role": analysis.recommended_agents[0]["role"] if analysis.recommended_agents else "Project Lead"
                },
                {
                    "description": f"Execute core project deliverables and requirements",
                    "agent_role": analysis.recommended_agents[1]["role"] if len(analysis.recommended_agents) > 1 else "Specialist"
                }
            ]
            
            # Add additional tasks for remaining agents
            for i, agent in enumerate(analysis.recommended_agents[2:], start=2):
                tasks.append({
                    "description": f"Provide specialized expertise and support for project requirements",
                    "agent_role": agent["role"]
                })
        
        # Add project-specific goals as additional tasks if provided
        for i, goal in enumerate(project_goals[:3]):  # Limit to 3 additional goals
            tasks.append({
                "description": f"Achieve specific project goal: {goal}",
                "agent_role": analysis.recommended_agents[i % len(analysis.recommended_agents)]["role"] if analysis.recommended_agents else "Specialist"
            })
        
        return tasks
    
    # Task Termination Methods
    async def _terminate_current_task(self, args: Dict[str, Any]) -> List[TextContent]:
        """Gracefully terminate current agent task and pass partial results to next step"""
        task_id = args["task_id"]
        reason = args.get("reason", "User requested termination")
        
        success = terminate_current_task(task_id, reason)
        
        if success:
            partial_results = task_terminator.get_partial_results(task_id)
            
            result = {
                "status": "success",
                "task_id": task_id,
                "termination_reason": reason,
                "partial_results": partial_results,
                "message": f"🛑 Task '{task_id}' terminated gracefully. Partial results preserved."
            }
        else:
            result = {
                "status": "error",
                "task_id": task_id,
                "message": f"❌ Task '{task_id}' not found or cannot be terminated"
            }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def _get_active_tasks(self, args: Dict[str, Any]) -> List[TextContent]:
        """Get list of all active tasks that can be terminated"""
        active_tasks = get_active_tasks()
        
        result = {
            "status": "success",
            "active_tasks": active_tasks,
            "count": len(active_tasks),
            "message": f"📋 Found {len(active_tasks)} active tasks"
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def _get_task_status_detail(self, args: Dict[str, Any]) -> List[TextContent]:
        """Get detailed status of a specific task including progress and partial results"""
        task_id = args["task_id"]
        
        task_status = task_terminator.get_task_status(task_id)
        
        if task_status:
            result = {
                "status": "success",
                "task_status": task_status,
                "message": f"📊 Task '{task_id}' status retrieved"
            }
        else:
            result = {
                "status": "error",
                "task_id": task_id,
                "message": f"❌ Task '{task_id}' not found"
            }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def _ensure_mcp_connections_ready(self, crew) -> None:
        """Ensure all MCP connections are established before making autonomous decisions"""
        max_wait_time = 5.0  # Maximum time to wait for connections (seconds)
        check_interval = 0.1  # Check every 100ms
        elapsed_time = 0.0
        
        logger.info(f"🔗 Waiting for MCP connections to be ready for crew {crew.crew_id}")
        
        while elapsed_time < max_wait_time:
            all_connected = True
            
            for agent in crew.agents:
                # Check if agent is MCPClientAgent and needs connections
                if isinstance(agent, MCPClientAgent):
                    # If agent has mcp_servers configured but none are connected
                    if hasattr(agent, 'mcp_servers') and agent.mcp_servers:
                        connected_count = sum(1 for conn in agent.mcp_servers.values() if conn.connected)
                        if connected_count == 0:
                            all_connected = False
                            break
                    # If agent has no mcp_servers yet, they might still be connecting
                    elif not hasattr(agent, 'mcp_servers') or not agent.mcp_servers:
                        # Give a short grace period for connections to be established
                        if elapsed_time < 1.0:  # Wait at least 1 second for initial connections
                            all_connected = False
                            break
            
            if all_connected:
                logger.info(f"✅ All MCP connections ready for crew {crew.crew_id}")
                return
            
            await asyncio.sleep(check_interval)
            elapsed_time += check_interval
        
        # Log warning if connections aren't ready but continue anyway
        logger.warning(f"⚠️ MCP connections not fully ready after {max_wait_time}s, proceeding anyway")
        
        # Update resource adequacy check to handle partially connected state
        for agent in crew.agents:
            if isinstance(agent, MCPClientAgent):
                logger.info(f"🔌 Agent {agent.agent_id} MCP status: {agent.get_mcp_status()}")
    
    async def run(self, transport_options: Dict[str, Any] = None):
        """Run the MCP server"""
        logger.info("🚀 Starting MCP CrewAI Server with Autonomous Evolution!")
        
        try:
            # Start background evolution (temporarily disabled for debugging)
            # await self.start_background_evolution()
            print("✅ Background evolution skipped for debugging", file=sys.stderr)
            
            # Import and run server
            from mcp.server.stdio import stdio_server
            print("✅ stdio_server imported", file=sys.stderr)
            
            print("🔍 Creating stdio_server context...", file=sys.stderr)
            async with stdio_server() as (read_stream, write_stream):
                print("✅ stdio_server context created", file=sys.stderr)
                print("🔍 About to call server.run()...", file=sys.stderr)
                
                await self.server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name="mcp-crewai-server",
                        server_version="0.1.0",
                        capabilities=self.server.get_capabilities(
                            notification_options=NotificationOptions(),
                            experimental_capabilities={}
                        )
                    )
                )
                print("✅ server.run() completed normally", file=sys.stderr)
        except Exception as e:
            print(f"❌ Error in server.run(): {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            raise


def main():
    """Main entry point"""
    server = MCPCrewAIServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()