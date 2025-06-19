#!/usr/bin/env python3
"""
MCP CrewAI Server - Main Entry Point
Real user-driven crew execution with Agent 1 building the crew
Now with autonomous agent evolution capabilities!
"""

import sys
import os
import asyncio

def main():
    """Main entry point - choose execution mode"""
    
    print("🔥 MCP CREWAI SERVER WITH EVOLUTION")
    print("=" * 50)
    
    # First let user choose LLM provider
    print("Choose LLM Provider:")
    print("1. Anthropic (Claude)")
    print("2. OpenAI (GPT)")
    print("3. Ollama (Local)")
    print("4. Google (Gemini)")
    print("5. Groq (Fast inference)")
    print("")
    
    try:
        llm_choice = input("Enter LLM choice (1-5) [default: 1]: ").strip()
        if not llm_choice:
            llm_choice = "1"
    except (EOFError, KeyboardInterrupt):
        llm_choice = "1"
    
    # Set LLM provider and get available models
    llm_providers = {
        "1": {
            "name": "anthropic",
            "display": "Anthropic (Claude)",
            "models": {
                "1": "claude-3-5-sonnet-20241022",
                "2": "claude-3-5-haiku-20241022", 
                "3": "claude-3-opus-20240229",
                "4": "claude-sonnet-4-20250514"
            }
        },
        "2": {
            "name": "openai", 
            "display": "OpenAI (GPT)",
            "models": {
                "1": "gpt-4o",
                "2": "gpt-4o-2024-08-06",
                "3": "gpt-4-turbo-preview",
                "4": "gpt-4",
                "5": "gpt-3.5-turbo"
            }
        },
        "3": {
            "name": "ollama",
            "display": "Ollama (Local)", 
            "models": {
                "1": "llama3.1:8b",
                "2": "llama3.1:70b",
                "3": "codellama:7b",
                "4": "mistral:7b",
                "5": "phi3:mini"
            }
        },
        "4": {
            "name": "google",
            "display": "Google (Gemini)",
            "models": {
                "1": "gemini-pro",
                "2": "gemini-1.5-pro",
                "3": "gemini-1.5-flash"
            }
        },
        "5": {
            "name": "groq",
            "display": "Groq (Fast inference)",
            "models": {
                "1": "llama-3.1-70b-versatile",
                "2": "llama-3.1-8b-instant", 
                "3": "mixtral-8x7b-32768",
                "4": "gemma-7b-it"
            }
        }
    }
    
    provider_config = llm_providers.get(llm_choice, llm_providers["1"])
    provider_name = provider_config["name"]
    provider_display = provider_config["display"]
    
    print(f"✅ Selected Provider: {provider_display}")
    print("\nChoose Model:")
    for key, model in provider_config["models"].items():
        print(f"{key}. {model}")
    print("")
    
    try:
        model_choice = input("Enter model choice [default: 1]: ").strip()
        if not model_choice:
            model_choice = "1"
    except (EOFError, KeyboardInterrupt):
        model_choice = "1"
    
    selected_model = provider_config["models"].get(model_choice, list(provider_config["models"].values())[0])
    
    os.environ['DEFAULT_LLM_PROVIDER'] = provider_name
    os.environ['DEFAULT_MODEL'] = selected_model
    
    print(f"✅ Selected: {provider_display} - {selected_model}")
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
            asyncio.run(run_evolving_crew_builder(goal))
        else:
            print(f"\n🧬 Running interactive evolving crew builder...")
            asyncio.run(run_evolving_crew_builder())
            
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

async def run_evolving_crew_builder(goal=None):
    """Run the evolving crew builder with Agent 1 research and evolution"""
    print("🧬 EVOLVING CREW BUILDER WITH AGENT 1")
    print("=" * 60)
    print("This enhanced version includes:")
    print("• Agent 1 researches and designs crew")
    print("• Hierarchical process with manager delegation")
    print("• Crew built with evolution capabilities")
    print("• Autonomous agent evolution during execution")
    print("• Performance monitoring and adaptation")
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
        
        # Create Agent 1 for research and design using selected LLM provider
        from src.mcp_crewai.server import create_llm
        llm = create_llm()
        web_search_tool = WebSearchTool()
        
        agent1 = Agent(
            role="Senior AI Crew Architecture Specialist",
            goal="""Conduct comprehensive research and design a highly specialized, hierarchical crew 
            configuration with precise role definitions, complementary skills, and clear task interfaces. 
            Deliver a detailed JSON specification that enables autonomous evolution and optimal performance.""",
            backstory="""You are a world-class AI system architect with 15+ years of experience designing 
            multi-agent systems for Fortune 500 companies. You've published research on agent collaboration 
            patterns, hierarchical team dynamics, and autonomous evolution frameworks. Your expertise includes:
            - Advanced agent role specialization and skill complementarity
            - Hierarchical delegation patterns and management structures  
            - Evolutionary AI systems and adaptation mechanisms
            - Task decomposition and interface design for seamless handoffs
            - Quality standards and performance optimization for AI teams
            
            You approach each project with scientific rigor, conducting thorough research before designing 
            highly specialized teams where each agent has distinct expertise that creates productive tension 
            and innovative solutions.""",
            tools=[web_search_tool],
            llm=llm,
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
                "process_type": "hierarchical",
                "management_strategy": "how the crew should be managed hierarchically",
                "agents": [
                    {{
                        "role": "Specific Role",
                        "goal": "Detailed goal related to: {goal}",
                        "backstory": "Backstory emphasizing adaptability, evolution, and hierarchical coordination",
                        "personality_type": "analytical|creative|collaborative|decisive",
                        "management_level": "manager|worker"
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
            expected_output="Detailed evolving crew configuration JSON",
            agent=agent1
        )
        
        # Create manager LLM for hierarchical process using selected provider
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
        
        # Execute with evolution using hierarchical process
        print("⚡ EXECUTING EVOLVING CREW WITH HIERARCHICAL MANAGEMENT & AUTONOMOUS ADAPTATION...")
        execution_context = {
            "user_goal": goal,
            "evolution_enabled": True,
            "process_type": "hierarchical",
            "research_analysis": config.get('research_analysis', ''),
            "evolution_strategy": config.get('evolution_strategy', '')
        }
        
        result = await server._run_autonomous_crew({
            "crew_id": crew_id,
            "context": execution_context, 
            "allow_evolution": True
        })
        
        # Show results
        print("\n🎉 EVOLVING CREW EXECUTION COMPLETED!")
        print("=" * 80)
        
        # Extract and display the actual work product
        if result:
            try:
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
        import json
        evolution_summary = await server._get_evolution_summary({})
        if evolution_summary:
            print("🧬 EVOLUTION SUMMARY:")
            evolution_data = json.loads(evolution_summary[0].text)
            print(f"   Total Evolutions: {evolution_data.get('total_evolutions', 0)}")
            print(f"   Evolution Rate: {evolution_data.get('evolution_rate', 0):.2f}%")
            print("")
        
        # Save results
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"exported_results/evolving_crew_results_{timestamp_str}.md"
        
        with open(filename, 'w') as f:
            f.write(f"# Evolving Crew Results\n\n")
            f.write(f"**Goal:** {goal}\n\n")
            f.write(f"**Agent 1 Analysis:** {config.get('research_analysis', 'N/A')}\n\n")
            f.write(f"**Evolution Strategy:** {config.get('evolution_strategy', 'N/A')}\n\n")
            f.write(f"**Process Type:** Hierarchical with autonomous evolution\n\n")
            f.write(f"**Management Strategy:** {config.get('management_strategy', 'Hierarchical coordination')}\n\n")
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