#!/usr/bin/env python3
"""
MCP CrewAI Server - Main Entry Point
Real user-driven crew execution with Agent 1 building the crew
Now with autonomous agent evolution capabilities!
"""

import sys
import os
import asyncio
import tiktoken
import subprocess
import json
from datetime import datetime

class TokenCounter:
    """Track tokens and calculate pricing for LLM API usage"""
    
    def __init__(self):
        self.session_input_tokens = 0
        self.session_output_tokens = 0
        self.session_start_time = datetime.now()
        self.input_price_per_million = float(os.getenv('MODEL_INPUT_PRICE', '0'))
        self.output_price_per_million = float(os.getenv('MODEL_OUTPUT_PRICE', '0'))
        
    def count_tokens(self, text: str, model: str = "gpt-4") -> int:
        """Count tokens in text using tiktoken"""
        try:
            # Use tiktoken for OpenAI models, estimate for others
            if "gpt" in model.lower() or "o1" in model.lower() or "o3" in model.lower():
                encoding = tiktoken.encoding_for_model(model.replace("gpt-4o", "gpt-4"))
                return len(encoding.encode(text))
            else:
                # Rough estimation: ~4 chars per token for other models
                return max(1, len(text) // 4)
        except Exception:
            # Fallback estimation
            return max(1, len(text) // 4)
    
    def add_usage(self, input_text: str, output_text: str, model: str):
        """Add token usage for a request"""
        input_tokens = self.count_tokens(input_text, model)
        output_tokens = self.count_tokens(output_text, model)
        
        self.session_input_tokens += input_tokens
        self.session_output_tokens += output_tokens
        
        input_cost = (input_tokens / 1_000_000) * self.input_price_per_million
        output_cost = (output_tokens / 1_000_000) * self.output_price_per_million
        total_cost = input_cost + output_cost
        
        print(f"📊 Token Usage: {input_tokens:,} input + {output_tokens:,} output = {input_tokens + output_tokens:,} total")
        print(f"💰 Request Cost: ${total_cost:.6f} (${input_cost:.6f} + ${output_cost:.6f})")
        
        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": total_cost
        }
    
    def get_session_summary(self):
        """Get session usage summary"""
        total_tokens = self.session_input_tokens + self.session_output_tokens
        total_input_cost = (self.session_input_tokens / 1_000_000) * self.input_price_per_million
        total_output_cost = (self.session_output_tokens / 1_000_000) * self.output_price_per_million
        total_session_cost = total_input_cost + total_output_cost
        
        duration = datetime.now() - self.session_start_time
        
        return {
            "session_duration": str(duration).split('.')[0],
            "total_input_tokens": self.session_input_tokens,
            "total_output_tokens": self.session_output_tokens,
            "total_tokens": total_tokens,
            "total_input_cost": total_input_cost,
            "total_output_cost": total_output_cost,
            "total_session_cost": total_session_cost
        }
    
    def print_session_summary(self):
        """Print formatted session summary"""
        summary = self.get_session_summary()
        
        print("\n" + "="*60)
        print("📊 SESSION USAGE SUMMARY")
        print("="*60)
        print(f"⏱️  Duration: {summary['session_duration']}")
        print(f"📥 Input tokens: {summary['total_input_tokens']:,}")
        print(f"📤 Output tokens: {summary['total_output_tokens']:,}")
        print(f"📊 Total tokens: {summary['total_tokens']:,}")
        print(f"💰 Input cost: ${summary['total_input_cost']:.6f}")
        print(f"💰 Output cost: ${summary['total_output_cost']:.6f}")
        print(f"💰 TOTAL COST: ${summary['total_session_cost']:.6f}")
        print("="*60)

# Global token counter instance
token_counter = TokenCounter()

def get_ollama_models():
    """Get actual Ollama models installed on the system"""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            models = {}
            model_count = 1
            
            # Skip header line and parse model names
            for line in lines[1:]:
                if line.strip():
                    # Extract model name (first column)
                    model_name = line.split()[0] if line.split() else None
                    if model_name and ':' in model_name:
                        models[str(model_count)] = {
                            "name": model_name,
                            "input_price": 0.0,
                            "output_price": 0.0,
                            "description": "Free (Local)"
                        }
                        model_count += 1
            
            if models:
                print(f"✅ Found {len(models)} Ollama models installed locally")
                return models
            else:
                return get_default_ollama_models()
        else:
            print("⚠️ Ollama not accessible, using default models")
            return get_default_ollama_models()
    except Exception as e:
        print(f"⚠️ Error checking Ollama models: {e}")
        return get_default_ollama_models()

def get_default_ollama_models():
    """Default Ollama models if system detection fails"""
    return {
        "1": {"name": "llama3.1:8b", "input_price": 0.0, "output_price": 0.0, "description": "Free (Local) - Pull with: ollama pull llama3.1:8b"},
        "2": {"name": "llama3.1:70b", "input_price": 0.0, "output_price": 0.0, "description": "Free (Local) - Pull with: ollama pull llama3.1:70b"},
        "3": {"name": "codellama:7b", "input_price": 0.0, "output_price": 0.0, "description": "Free (Local) - Pull with: ollama pull codellama:7b"},
        "4": {"name": "mistral:7b", "input_price": 0.0, "output_price": 0.0, "description": "Free (Local) - Pull with: ollama pull mistral:7b"},
        "5": {"name": "phi3:mini", "input_price": 0.0, "output_price": 0.0, "description": "Free (Local) - Pull with: ollama pull phi3:mini"}
    }

def main():
    """Main entry point - choose execution mode"""
    
    print("🔥 MCP CREWAI SERVER WITH EVOLUTION")
    print("=" * 50)
    
    # First let user choose LLM provider
    print("Choose LLM Provider:")
    print("1. Ollama (Local)")
    print("2. Anthropic (Claude)")
    print("3. OpenAI (GPT)")
    print("4. Google (Gemini)")
    print("5. Groq (Fast inference)")
    print("")
    
    try:
        llm_choice = input("Enter LLM choice (1-5) [default: 1]: ").strip()
        if not llm_choice:
            llm_choice = "1"
    except (EOFError, KeyboardInterrupt):
        llm_choice = "1"
    
    # Set LLM provider and get available models with real pricing (per million tokens)
    ollama_models = get_ollama_models()
    
    llm_providers = {
        "1": {
            "name": "ollama",
            "display": "Ollama (Local)", 
            "models": ollama_models
        },
        "2": {
            "name": "anthropic",
            "display": "Anthropic (Claude)",
            "models": {
                "1": {"name": "claude-3-5-sonnet-20241022", "input_price": 3.0, "output_price": 15.0, "description": "$3/$15 per MTok"},
                "2": {"name": "claude-3-5-haiku-20241022", "input_price": 0.8, "output_price": 4.0, "description": "$0.8/$4 per MTok"},
                "3": {"name": "claude-3-opus-20240229", "input_price": 15.0, "output_price": 75.0, "description": "$15/$75 per MTok"},
                "4": {"name": "claude-3-sonnet-20240229", "input_price": 3.0, "output_price": 15.0, "description": "$3/$15 per MTok (Legacy)"},
                "5": {"name": "claude-3-haiku-20240307", "input_price": 0.25, "output_price": 1.25, "description": "$0.25/$1.25 per MTok (Legacy)"}
            }
        },
        "3": {
            "name": "openai", 
            "display": "OpenAI (GPT)",
            "models": {
                "1": {"name": "gpt-4o", "input_price": 5.0, "output_price": 15.0, "description": "$5/$15 per MTok"},
                "2": {"name": "gpt-4o-mini", "input_price": 0.15, "output_price": 0.6, "description": "$0.15/$0.6 per MTok"},
                "3": {"name": "o1-pro", "input_price": 150.0, "output_price": 600.0, "description": "$150/$600 per MTok"},
                "4": {"name": "o3-mini", "input_price": 1.1, "output_price": 4.4, "description": "$1.1/$4.4 per MTok"},
                "5": {"name": "gpt-4-turbo", "input_price": 10.0, "output_price": 30.0, "description": "$10/$30 per MTok"},
                "6": {"name": "gpt-3.5-turbo", "input_price": 0.5, "output_price": 1.5, "description": "$0.5/$1.5 per MTok"}
            }
        },
        "4": {
            "name": "google",
            "display": "Google (Gemini)",
            "models": {
                "1": {"name": "gemini-2.0-flash", "input_price": 0.1, "output_price": 0.4, "description": "$0.1/$0.4 per MTok"},
                "2": {"name": "gemini-1.5-pro", "input_price": 1.25, "output_price": 5.0, "description": "$1.25/$5 per MTok"},
                "3": {"name": "gemini-1.5-flash", "input_price": 0.075, "output_price": 0.3, "description": "$0.075/$0.3 per MTok"},
                "4": {"name": "gemini-1.5-flash-8b", "input_price": 0.0375, "output_price": 0.15, "description": "$0.0375/$0.15 per MTok"}
            }
        },
        "5": {
            "name": "groq",
            "display": "Groq (Fast inference)",
            "models": {
                "1": {"name": "llama-3.1-70b-versatile", "input_price": 0.59, "output_price": 0.79, "description": "$0.59/$0.79 per MTok"},
                "2": {"name": "llama-3.1-8b-instant", "input_price": 0.05, "output_price": 0.08, "description": "$0.05/$0.08 per MTok"},
                "3": {"name": "mixtral-8x7b-32768", "input_price": 0.24, "output_price": 0.24, "description": "$0.24/$0.24 per MTok"},
                "4": {"name": "gemma-7b-it", "input_price": 0.07, "output_price": 0.07, "description": "$0.07/$0.07 per MTok"},
                "5": {"name": "llama3-70b-8192", "input_price": 0.59, "output_price": 0.79, "description": "$0.59/$0.79 per MTok"}
            }
        }
    }
    
    provider_config = llm_providers.get(llm_choice, llm_providers["1"])
    provider_name = provider_config["name"]
    provider_display = provider_config["display"]
    
    print(f"✅ Selected Provider: {provider_display}")
    print("\nChoose Model:")
    for key, model_data in provider_config["models"].items():
        # Calculate estimated cost for 100k tokens (typical session)
        est_cost_100k = (50000 * model_data['input_price'] + 50000 * model_data['output_price']) / 1000000
        cost_display = f"(~${est_cost_100k:.4f} per 100k tokens)" if est_cost_100k > 0 else ""
        print(f"{key}. {model_data['name']} - {model_data['description']} {cost_display}")
    print("")
    
    try:
        model_choice = input("Enter model choice [default: 1]: ").strip()
        if not model_choice:
            model_choice = "1"
    except (EOFError, KeyboardInterrupt):
        model_choice = "1"
    
    selected_model_data = provider_config["models"].get(model_choice, list(provider_config["models"].values())[0])
    selected_model = selected_model_data["name"]
    selected_input_price = selected_model_data["input_price"]
    selected_output_price = selected_model_data["output_price"]
    
    os.environ['DEFAULT_LLM_PROVIDER'] = provider_name
    os.environ['DEFAULT_MODEL'] = selected_model
    os.environ['MODEL_INPUT_PRICE'] = str(selected_input_price)
    os.environ['MODEL_OUTPUT_PRICE'] = str(selected_output_price)
    
    # Verify provider-specific requirements
    if provider_name == "ollama":
        try:
            result = subprocess.run(['ollama', 'ps'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("✅ Ollama service is running")
            else:
                print("⚠️ Warning: Ollama service may not be running. Start with: ollama serve")
        except Exception:
            print("⚠️ Warning: Could not verify Ollama status")
    elif provider_name == "anthropic":
        if not os.getenv('ANTHROPIC_API_KEY'):
            print("⚠️ Warning: ANTHROPIC_API_KEY environment variable not set")
            print("   Set it with: export ANTHROPIC_API_KEY=your_api_key")
        else:
            print("✅ Anthropic API key found")
    
    # Initialize token counter with selected model pricing
    global token_counter
    token_counter = TokenCounter()
    
    print(f"✅ Selected: {provider_display} - {selected_model}")
    print(f"💰 Pricing: ${selected_input_price}/${selected_output_price} per MTok (input/output)")
    print("📊 Token usage tracking enabled")
    print("")
    
    print("Choose execution mode:")
    print("1. Crew Builder (Agent 1 designs crew)")
    print("2. MCP Server (Start MCP server)")
    print("3. Examples (Run example scripts)")
    print("4. Evolution Demo (Show autonomous agent evolution)")
    print("5. Flow-Based Builder (Advanced CrewAI Flow orchestration)")
    print("")
    
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
    else:
        try:
            mode = input("Enter choice (1-5): ").strip()
        except (EOFError, KeyboardInterrupt):
            mode = "1"  # Default to crew builder
    
    if mode in ["1", "crew", "builder"]:
        # Run evolving crew builder
        goal_args = sys.argv[2:] if len(sys.argv) > 2 else []
        if goal_args:
            goal = " ".join(goal_args)
            print(f"\n🧬 Running evolving crew builder with goal: {goal}")
            asyncio.run(run_evolving_crew_builder(goal, provider_name, selected_model))
        else:
            print(f"\n🧬 Running interactive evolving crew builder...")
            asyncio.run(run_evolving_crew_builder(None, provider_name, selected_model))
            
    elif mode in ["2", "server", "mcp"]:
        # Start MCP server
        from src.mcp_crewai.server import main as server_main
        server_main()
        
    elif mode in ["3", "examples", "demo"]:
        # Show examples
        print("\n📁 Available examples:")
        print("- examples/verbose_crew_execution.py")
        print("- examples/simple_crew_interface.py") 
        print("- tools/real_crewai_execution.py")
        print("- examples/demo_revolutionary_features.py")
        print("\nRun: python3 examples/<script_name>")
        
    elif mode in ["4", "evolution", "evolve"]:
        # Evolution demo
        print("\n🧬 STARTING AUTONOMOUS AGENT EVOLUTION DEMO...")
        asyncio.run(run_evolution_demo())
        
    elif mode in ["5", "flow", "flows"]:
        # Flow-based crew builder
        print("\n🧬 FLOW-BASED CREW BUILDER WITH EVOLUTION")
        print("=" * 60)
        print("This advanced version includes:")
        print("• CrewAI Flow orchestration with state management")
        print("• Agent 1 research and crew design")
        print("• Autonomous agent evolution during execution")
        print("• Advanced error handling and recovery")
        print("• Comprehensive result extraction")
        print("")
        
        goal_args = sys.argv[2:] if len(sys.argv) > 2 else []
        if goal_args:
            goal = " ".join(goal_args)
            print(f"🎯 Goal provided: {goal}")
            from evolving_crew_flow import run_flow_based_crew_builder
            run_flow_based_crew_builder(goal)
        else:
            print("🎯 INTERACTIVE MODE: You will be prompted for your goal...")
            from evolving_crew_flow import run_flow_based_crew_builder
            run_flow_based_crew_builder()
        
    else:
        print("❌ Invalid choice. Using flow-based crew builder...")
        from evolving_crew_flow import run_flow_based_crew_builder
        run_flow_based_crew_builder()
    
    # Print session usage summary at the end
    if token_counter.session_input_tokens > 0 or token_counter.session_output_tokens > 0:
        token_counter.print_session_summary()

async def run_evolution_demo():
    """Run autonomous agent evolution demonstration"""
    print("🧬 AUTONOMOUS AGENT EVOLUTION DEMONSTRATION")
    print("=" * 60)
    
    try:
        from examples.demo_revolutionary_features import demo_1_evolving_personalities
        await demo_1_evolving_personalities()
        
        print("\n🎉 EVOLUTION Demo Completed!")
        print("📊 Check the console output above to see how agents evolved")
        print("📁 Evolution data is stored in evolution_history.db")
        
    except Exception as e:
        print(f"❌ Evolution demo failed: {e}")
        import traceback
        traceback.print_exc()

def parse_agent1_config(agent1_result):
    """Parse Agent 1's crew configuration - ACTUALLY USE AGENT 1'S OUTPUT"""
    import json
    
    print(f"\n📊 PARSING AGENT 1'S CREW DESIGN")
    print("-" * 50)
    
    print("🔍 Agent 1's Full Response:")
    print("-" * 30)
    print(agent1_result)
    print("-" * 30)
    
    # Try to extract JSON from Agent 1's response
    try:
        # Look for JSON in the response - try multiple patterns
        json_patterns = [
            (agent1_result.find('```json'), agent1_result.find('```', agent1_result.find('```json') + 7)),
            (agent1_result.find('{'), agent1_result.rfind('}') + 1),
        ]
        
        for start_marker, end_marker in json_patterns:
            if start_marker != -1 and end_marker != -1:
                if start_marker == agent1_result.find('```json'):
                    # JSON in code block
                    json_str = agent1_result[start_marker + 7:end_marker]
                else:
                    # Direct JSON
                    json_str = agent1_result[start_marker:end_marker]
                
                # Clean up the JSON string
                json_str = json_str.strip()
                
                print(f"🔍 Extracted JSON string:")
                print(json_str[:200] + "..." if len(json_str) > 200 else json_str)
                
                config = json.loads(json_str)
                
                print("✅ SUCCESS: Parsed Agent 1's actual crew configuration!")
                print(f"   Research Analysis: {config.get('research_analysis', 'N/A')[:100]}...")
                print(f"   Agents: {len(config.get('agents', []))}")
                print(f"   Tasks: {len(config.get('tasks', []))}")
                
                return config
                
    except Exception as e:
        print(f"❌ ERROR parsing Agent 1's JSON: {e}")
        print("🔍 JSON parsing failed - showing Agent 1's output for debugging:")
        print(agent1_result)
        
    # ONLY if we absolutely cannot parse Agent 1's response
    print("❌ CRITICAL ERROR: Could not parse Agent 1's configuration")
    print("This should not happen - Agent 1 should provide valid JSON")
    import sys
    sys.exit(1)

async def run_evolving_crew_builder(goal=None, provider_name="ollama", selected_model="mistral:latest"):
    """Run the evolving crew builder with Agent 1 research and evolution"""
    print("🧬 EVOLVING CREW BUILDER WITH AGENT 1")
    print("=" * 60)
    
    # Calculate dynamic stats
    total_providers = 5  # Ollama, Anthropic, OpenAI, Google, Groq
    
    print("🚀 REVOLUTIONARY AI CREW SYSTEM:")
    if provider_name == "ollama":
        ollama_count = len(get_ollama_models())
        print(f"• {ollama_count} Local Ollama models detected + {total_providers-1} cloud providers available")
        print(f"• Zero-cost execution: $0.0/$0.0 per MTok (FREE!)")
    else:
        input_price = os.getenv('MODEL_INPUT_PRICE', '0')
        output_price = os.getenv('MODEL_OUTPUT_PRICE', '0')
        print(f"• {total_providers} LLM providers available (Ollama, Anthropic, OpenAI, Google, Groq)")
        print(f"• Real-time token tracking: ${input_price}/${output_price} per MTok")
    print(f"• Selected: {provider_name.title()} - {selected_model}")
    print(f"• Agent 1 researches web + designs optimal crew architecture")
    print(f"• Evolution engine: Agents adapt and improve during execution")
    print("")
    
    try:
        # Import required modules
        from crewai import Agent, Task, Crew, Process
        from crewai.tools import BaseTool
        import requests
        from src.mcp_crewai.server import MCPCrewAIServer
        
        # Use existing WebSearchTool from the original code
        class WebSearchTool(BaseTool):
            """Web search tool using Brave Search API"""
            name: str = "web_search"
            description: str = "Search the internet for information about any topic"
            
            def _run(self, query: str) -> str:
                """Search the web for information"""
                print(f"🔍 WEB SEARCH: {query}")
                
                brave_api_key = os.getenv('BRAVE_API_KEY')
                if not brave_api_key:
                    return "Web search not available - no API key"
                
                try:
                    url = "https://api.search.brave.com/res/v1/web/search"
                    headers = {
                        "Accept": "application/json",
                        "Accept-Encoding": "gzip",
                        "X-Subscription-Token": brave_api_key
                    }
                    params = {
                        "q": query,
                        "count": 5,
                        "text_decorations": False,
                        "search_lang": "en",
                        "country": "US",
                        "safesearch": "moderate"
                    }
                    
                    response = requests.get(url, headers=headers, params=params, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        results = []
                        
                        if 'web' in data and 'results' in data['web']:
                            for result in data['web']['results'][:5]:
                                title = result.get('title', 'No title')
                                description = result.get('description', 'No description')
                                url = result.get('url', 'No URL')
                                results.append(f"**{title}**\n{description}\nURL: {url}\n")
                        
                        search_results = f"🔍 Web Search Results for '{query}':\n\n" + "\n".join(results)
                        print(f"✅ WEB SEARCH COMPLETE: Found {len(results)} results")
                        return search_results
                    else:
                        return f"Web search failed with status code: {response.status_code}"
                        
                except Exception as e:
                    print(f"❌ Web search error: {e}")
                    return f"Web search error: {str(e)}"
        
        # Get user goal if not provided
        if not goal:
            print("🎯 AGENT 1 WILL RESEARCH AND DESIGN YOUR EVOLVING CREW")
            print("=" * 60)
            print("Please describe what you want the AI crew to accomplish:")
            print("(e.g., 'Create a marketing strategy for a new product', 'Write a technical documentation', etc.)")
            print("")
            try:
                while True:
                    goal = input("Your request: ").strip()
                    if goal:
                        break
                    print("❌ Please provide a valid request. This field is required.")
                    print("")
            except (EOFError, KeyboardInterrupt):
                print("\n❌ Operation cancelled by user.")
                return
        
        print(f"🔍 Agent 1 will research this goal and design the optimal evolving crew: {goal}")
        
        # Create Agent 1 for research and design using CrewAI's native LLM configuration
        web_search_tool = WebSearchTool()
        
        # Use CrewAI's LLM class for better compatibility
        if provider_name == "ollama":
            from crewai import LLM
            crew_llm = LLM(
                model=f"ollama/{selected_model}",
                base_url="http://localhost:11434"
            )
            print(f"✅ Using CrewAI LLM wrapper for Ollama: {selected_model}")
        elif provider_name == "anthropic":
            from crewai import LLM
            crew_llm = LLM(
                model=f"anthropic/{selected_model}",
                api_key=os.getenv('ANTHROPIC_API_KEY')
            )
            print(f"✅ Using CrewAI LLM wrapper for Anthropic: {selected_model}")
        else:
            # For other providers, use our create_llm function
            from src.mcp_crewai.server import create_llm
            crew_llm = create_llm()
        
        agent1 = Agent(
            role="Senior AI Crew Architecture Specialist",
            goal="""Conduct comprehensive research and design a highly specialized crew configuration 
            with precise role definitions, complementary skills, and clear task interfaces. Choose the optimal 
            process type (sequential or hierarchical) based on the task complexity and coordination needs.
            Deliver a detailed JSON specification that enables autonomous evolution and optimal performance.""",
            backstory="""You are a world-class AI system architect with 15+ years of experience designing 
            multi-agent systems for Fortune 500 companies. You've published research on agent collaboration 
            patterns, team dynamics, and autonomous evolution frameworks. Your expertise includes:
            - Advanced agent role specialization and skill complementarity
            - Process optimization (sequential vs hierarchical coordination)
            - Evolutionary AI systems and adaptation mechanisms
            - Task decomposition and interface design for seamless handoffs
            - Quality standards and performance optimization for AI teams
            
            You understand that SEQUENTIAL processes work best for linear workflows where tasks build on each other,
            while HIERARCHICAL processes are optimal for complex coordination requiring management oversight.
            
            You approach each project with scientific rigor, conducting thorough research before designing 
            highly specialized teams where each agent has distinct expertise that creates productive solutions.""",
            tools=[web_search_tool],
            llm=crew_llm,
            verbose=True,
            allow_delegation=False
        )
        
        # Create research task
        research_task = Task(
            description=f"""
            Research and design an evolving crew for: {goal}
            
            RESEARCH PHASE:
            1. Search internet for context about: {goal}
            2. Analyze what skills and roles are needed
            3. Consider how agents might need to evolve and adapt
            4. Design crew with evolution capabilities in mind
            
            DESIGN PHASE:
            Create a crew configuration as JSON with:
            {{
                "research_analysis": "your analysis of requirements",
                "evolution_strategy": "how agents should evolve for this goal",
                "process_type": "sequential|hierarchical (choose based on: sequential=linear workflow, hierarchical=complex coordination)",
                "management_strategy": "how the crew should be managed (describe the coordination approach)",
                "agents": [
                    {{
                        "role": "Specific Role",
                        "goal": "Detailed goal related to: {goal}",
                        "backstory": "Backstory emphasizing adaptability and evolution",
                        "personality_type": "analytical|creative|collaborative|decisive",
                        "management_level": "manager|worker (only needed if process_type is hierarchical)"
                    }}
                ],
                "tasks": [
                    {{
                        "description": "Task description",
                        "expected_output": "Expected output"
                    }}
                ]
            }}
            """,
            expected_output="MUST return valid JSON configuration ONLY. No explanation, just the JSON object starting with { and ending with }.",
            agent=agent1
        )
        
        # Create manager LLM for hierarchical process using selected provider
        if provider_name == "ollama":
            manager_llm = LLM(
                model=f"ollama/{selected_model}",
                base_url="http://localhost:11434"
            )
        elif provider_name == "anthropic":
            manager_llm = LLM(
                model=f"anthropic/{selected_model}",
                api_key=os.getenv('ANTHROPIC_API_KEY')
            )
        else:
            from src.mcp_crewai.server import create_llm
            manager_llm = create_llm()
        
        # Execute Agent 1's research
        research_crew = Crew(
            agents=[agent1],
            tasks=[research_task],
            verbose=True,
            process=Process.hierarchical,
            manager_llm=manager_llm
        )
        
        print("🔍 AGENT 1 RESEARCHING AND DESIGNING EVOLVING CREW...")
        agent1_result = research_crew.kickoff()
        print("✅ AGENT 1 RESEARCH COMPLETED!")
        
        # Track token usage for Agent 1's research
        input_text = f"{research_task.description}\n{agent1.backstory}\n{goal}"
        output_text = str(agent1_result)
        token_counter.add_usage(input_text, output_text, os.getenv('DEFAULT_MODEL', 'gpt-4'))
        
        # Parse configuration
        config = parse_agent1_config(str(agent1_result))
        
        # Create evolving crew
        server = MCPCrewAIServer()
        
        # Convert to evolution format
        agents_config = []
        for agent_config in config['agents']:
            personality_preset = agent_config.get('personality_type', 'collaborative')
            if personality_preset not in ['analytical', 'creative', 'collaborative', 'decisive']:
                personality_preset = 'collaborative'
                
            agents_config.append({
                "role": agent_config['role'],
                "goal": agent_config['goal'],
                "backstory": agent_config['backstory'],
                "personality_preset": personality_preset
            })
        
        from datetime import datetime
        timestamp = int(datetime.now().timestamp())
        crew_config = {
            "crew_name": f"evolving_crew_{timestamp}",
            "agents_config": agents_config,
            "tasks": config['tasks'],
            "autonomy_level": 0.8  # High autonomy for maximum evolution
        }
        
        print("🧬 CREATING EVOLVING CREW...")
        await server._create_evolving_crew(crew_config)
        crew_id = crew_config["crew_name"]
        
        # Execute with evolution using Agent 1's chosen process type
        chosen_process = config.get('process_type', 'sequential').lower()
        process_display = "HIERARCHICAL MANAGEMENT" if chosen_process == "hierarchical" else "SEQUENTIAL WORKFLOW"
        print(f"⚡ EXECUTING EVOLVING CREW WITH {process_display} & AUTONOMOUS ADAPTATION...")
        execution_context = {
            "user_goal": goal,
            "evolution_enabled": True,
            "process_type": chosen_process,
            "research_analysis": config.get('research_analysis', ''),
            "evolution_strategy": config.get('evolution_strategy', '')
        }
        
        result = await server._run_autonomous_crew({
            "crew_id": crew_id,
            "context": execution_context, 
            "allow_evolution": True
        })
        
        # Track token usage for crew execution (estimate based on goal and result)
        if result:
            crew_input_text = f"{goal}\n{config.get('research_analysis', '')}\n{str(execution_context)}"
            crew_output_text = str(result[0].text) if result else ""
            token_counter.add_usage(crew_input_text, crew_output_text, os.getenv('DEFAULT_MODEL', 'gpt-4'))
        
        # Show results
        print("\n🎉 EVOLVING CREW EXECUTION COMPLETED!")
        print("=" * 80)
        
        # Extract and display the actual work product
        if result:
            try:
                import json
                result_data = json.loads(result[0].text)
                
                # Check if we have deliverable results
                if result_data.get("status") == "completed" and "deliverable_results" in result_data:
                    deliverables = result_data["deliverable_results"]
                    outputs = deliverables.get("outputs", [])
                    
                    print("\n📝 ACTUAL WORK PRODUCTS:")
                    print("=" * 60)
                    
                    for i, output in enumerate(outputs, 1):
                        task_desc = output.get("description", f"Task {i}")
                        agent_name = output.get("assigned_agent", "Unknown Agent") 
                        content = output.get("result", "No content")
                        
                        print(f"\n🔹 Task {i}: {task_desc}")
                        print(f"👤 Agent: {agent_name}")
                        print(f"📄 Output:")
                        print("-" * 40)
                        print(content)
                        print("-" * 40)
                    
                    # Show file exports if any
                    files = deliverables.get("files_generated", [])
                    if files:
                        print(f"\n📁 EXPORTED FILES:")
                        for file_info in files:
                            print(f"   - {file_info.get('file_path', 'Unknown file')}")
                    
                    # Save the actual content to the summary
                    actual_work_content = "\n\n".join([
                        f"## {output.get('description', f'Task {i+1}')}\n"
                        f"**Agent:** {output.get('assigned_agent', 'Unknown')}\n\n"
                        f"{output.get('result', 'No content')}"
                        for i, output in enumerate(outputs)
                    ])
                    
                else:
                    print(f"\n⚠️ Crew status: {result_data.get('status', 'unknown')}")
                    print("No completed deliverables found.")
                    actual_work_content = f"System response: {result[0].text}"
                    
            except Exception as e:
                print(f"❌ Error extracting work products: {e}")
                actual_work_content = f"Raw result: {result[0].text if result else 'No result'}"
        else:
            actual_work_content = "No result returned from crew execution"
        
        # Get evolution summary
        evolution_summary = await server._get_evolution_summary({})
        if evolution_summary:
            print("🧬 EVOLUTION SUMMARY:")
            import json
            evolution_data = json.loads(evolution_summary[0].text)
            print(f"   Total Evolutions: {evolution_data.get('total_evolutions', 0)}")
            print(f"   Evolution Rate: {evolution_data.get('evolution_rate', 0):.2f}%")
            print("")
        
        # Save results
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("exported_results", exist_ok=True)
        filename = f"exported_results/evolving_crew_results_{timestamp_str}.md"
        
        with open(filename, 'w') as f:
            import json
            f.write(f"# Evolving Crew Results\n\n")
            f.write(f"**Goal:** {goal}\n\n")
            f.write(f"**Agent 1 Analysis:** {config.get('research_analysis', 'N/A')}\n\n")
            f.write(f"**Evolution Strategy:** {config.get('evolution_strategy', 'N/A')}\n\n")
            f.write(f"**Process Type:** {chosen_process.title()} with autonomous evolution\n\n")
            f.write(f"**Management Strategy:** {config.get('management_strategy', 'Agent coordination')}\n\n")
            f.write(f"**Crew Configuration:**\n```json\n{json.dumps(crew_config, indent=2)}\n```\n\n")
            if evolution_summary:
                f.write(f"**Evolution Summary:**\n```json\n{evolution_summary[0].text}\n```\n\n")
            f.write(f"**Final Work Products:**\n\n")
            f.write(actual_work_content)
            f.write(f"\n\n**System Metadata:**\n\n")
            f.write(str(result[0].text) if result else "No result available")
        
        print(f"💾 Results saved to: {filename}")
        print(f"🧬 Agents evolved autonomously during execution!")
        
    except Exception as e:
        print(f"❌ Evolving crew builder failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()