#!/usr/bin/env python3
"""
AGENT 1 BUILDS REAL CREW - SIMPLIFIED VERSION
Agent 1 researches and determines crew configuration, then we build it
"""

import os
import sys
import json
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Ensure exported_results directory exists
os.makedirs('exported_results', exist_ok=True)

# Check API keys
print(f"🔑 Checking API Keys...")
openai_key = os.getenv('OPENAI_API_KEY')
if openai_key:
    print(f"✅ OpenAI API Key: {openai_key[:10]}...{openai_key[-4:]}")
else:
    print("❌ OpenAI API Key not found!")
    sys.exit(1)

from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool
from langchain_openai import ChatOpenAI
import requests

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

def get_user_goal():
    """Get user's goal"""
    print("🎯 AGENT 1 WILL RESEARCH AND DESIGN YOUR CREW")
    print("=" * 60)
    
    # Check command line argument
    if len(sys.argv) > 1:
        goal = " ".join(sys.argv[1:]).strip()
        print(f"Goal: {goal}")
    else:
        goal = "Create a comprehensive FAQ for Cyanview CI0"
        print(f"Default goal: {goal}")
    
    print("🔍 Agent 1 will research this goal and design the optimal crew...")
    return goal

def run_agent1_research(user_goal):
    """Agent 1 researches and designs crew configuration"""
    print(f"\n🤖 AGENT 1 RESEARCHING AND DESIGNING CREW")
    print("=" * 60)
    
    # Create Agent 1 - the crew designer with web search tool
    llm = ChatOpenAI(model="gpt-4o-2024-08-06", temperature=0.8, verbose=True)
    web_search_tool = WebSearchTool()
    
    agent1 = Agent(
        role="AI Crew Research Architect",
        goal="Research user goals thoroughly using web search and design the optimal multi-agent crew configuration",
        backstory="""You are an expert AI system architect who specializes in analyzing 
        user requirements through internet research and designing optimal multi-agent crews. You have deep knowledge of:
        - Internet search, search engines, and web research
        - Different agent roles and their optimal configurations
        - LLM temperature settings for different tasks (0.1-0.3 analytical, 0.7-0.9 creative)
        - Agent backstories that maximize effectiveness
        - Crew composition and task design principles
        
        You always start by researching the user's goal on the internet to understand the context,
        then design the perfect crew configuration based on your findings.""",
        tools=[web_search_tool],
        llm=llm,
        verbose=True,
        allow_delegation=False
    )
    
    # Create research task
    research_task = Task(
        description=f"""
        Research this user goal and design the optimal crew: {user_goal}
        
        RESEARCH PHASE:
        1. search Internet what the {user_goal} is about, use it as context for next steps
        2. cleverly analyze what this goal requires (technical knowledge, creativity, research, writing, etc.)
        3. Determine what types of agents would be most effective
        4. Research optimal temperature settings for each agent type
        5. Design specific roles, goals, and backstories
        
        DESIGN PHASE:
        Create a detailed crew configuration as a JSON structure with:
        
        {{
            "research_analysis": "your analysis of what this goal requires",
            "crew_rationale": "why you chose this specific crew composition",
            "agents": [
                {{
                    "role": "Specific Agent Role",
                    "goal": "Detailed goal for this agent related to: {user_goal}",
                    "backstory": "Comprehensive backstory that makes this agent highly effective",
                    "temperature": 0.7,
                    "rationale": "why this temperature and role are optimal"
                }}
            ],
            "tasks": [
                {{
                    "description": "Detailed task description",
                    "expected_output": "Specific expected output",
                    "rationale": "why this task is needed"
                }}
            ],
            "execution_strategy": "how the crew should work together"
        }}
        
        Be very specific and detailed. This configuration will be used to build the actual crew.
        """,
        expected_output="Detailed crew configuration JSON with research analysis and rationale",
        agent=agent1
    )
    
    # Execute Agent 1's research
    research_crew = Crew(
        agents=[agent1],
        tasks=[research_task],
        verbose=True,
        process=Process.sequential
    )
    
    print("🔍 AGENT 1 STARTING RESEARCH...")
    
    result = research_crew.kickoff()
    
    print(f"\n✅ AGENT 1 COMPLETED RESEARCH!")
    print("=" * 60)
    
    return str(result)

def parse_agent1_config(agent1_result):
    """Parse Agent 1's crew configuration - ACTUALLY USE AGENT 1'S OUTPUT"""
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
    sys.exit(1)

def build_agent1_crew(config, user_goal):
    """Build the crew based on Agent 1's configuration"""
    print(f"\n🏗️ BUILDING CREW FROM AGENT 1'S DESIGN")
    print("=" * 60)
    
    print("📊 Agent 1's Analysis:")
    print(f"   Research: {config.get('research_analysis', 'N/A')}")
    print(f"   Rationale: {config.get('crew_rationale', 'N/A')}")
    print("")
    
    # Build agents according to Agent 1's specifications
    agents = []
    web_search_tool = WebSearchTool()
    
    for agent_config in config['agents']:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=agent_config['temperature'],
            verbose=True
        )
        
        agent = Agent(
            role=agent_config['role'],
            goal=agent_config['goal'],
            backstory=agent_config['backstory'],
            tools=[web_search_tool],  # Give all agents web search capability
            llm=llm,
            verbose=True,
            allow_delegation=False
        )
        agents.append(agent)
        
        print(f"✅ Created agent per Agent 1's design:")
        print(f"   Role: {agent.role}")
        print(f"   Temperature: {agent_config['temperature']} ({agent_config.get('rationale', 'N/A')})")
        print(f"   Goal: {agent.goal}")
        print(f"   🔧 Tools: Web search enabled")
        print("")
    
    # Build tasks according to Agent 1's specifications
    tasks = []
    for i, task_config in enumerate(config['tasks']):
        task = Task(
            description=task_config['description'],
            expected_output=task_config['expected_output'],
            agent=agents[i] if i < len(agents) else agents[0]
        )
        tasks.append(task)
        
        print(f"✅ Created task per Agent 1's design:")
        print(f"   Description: {task_config['description'][:60]}...")
        print(f"   Rationale: {task_config.get('rationale', 'N/A')}")
        print("")
    
    # Build crew according to Agent 1's strategy
    crew = Crew(
        agents=agents,
        tasks=tasks,
        verbose=True,
        process=Process.sequential,
        memory=True
    )
    
    print(f"🚀 EXECUTING AGENT 1'S CREW DESIGN")
    print(f"Strategy: {config.get('execution_strategy', 'Sequential execution')}")
    print("")
    
    return crew

def execute_agent1_crew(crew, config, user_goal):
    """Execute the crew that Agent 1 designed"""
    print(f"⚡ EXECUTING CREW DESIGNED BY AGENT 1...")
    print("👁️ MAXIMUM VERBOSITY - WATCH THE CREW WORK!")
    print("")
    
    try:
        # Execute Agent 1's crew design
        result = crew.kickoff()
        
        print(f"\n🎉 AGENT 1'S CREW EXECUTION COMPLETED!")
        print("=" * 80)
        
        # Save complete results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"exported_results/agent1_designed_crew_{timestamp}.md"
        
        with open(filename, 'w') as f:
            f.write(f"# Agent 1 Designed and Executed Crew\n\n")
            f.write(f"**User Goal:** {user_goal}\n\n")
            f.write(f"**Agent 1's Research Analysis:**\n{config.get('research_analysis', 'N/A')}\n\n")
            f.write(f"**Agent 1's Crew Rationale:**\n{config.get('crew_rationale', 'N/A')}\n\n")
            f.write(f"**Agent 1's Execution Strategy:**\n{config.get('execution_strategy', 'N/A')}\n\n")
            f.write(f"**Execution Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Crew Configuration:**\n```json\n{json.dumps(config, indent=2)}\n```\n\n")
            f.write(f"**Final Result:**\n\n")
            f.write(str(result))
        
        print(f"💾 Complete work saved to: {filename}")
        print(f"📊 Result length: {len(str(result))} characters")
        
        # Show preview
        preview = str(result)[:1000] + "..." if len(str(result)) > 1000 else str(result)
        print(f"\n📖 FINAL RESULT PREVIEW:")
        print("-" * 60)
        print(preview)
        
        return result
        
    except Exception as e:
        print(f"❌ Crew execution failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main execution"""
    print("🔥 AGENT 1 RESEARCHES, DESIGNS, AND EXECUTES CREW")
    print("=" * 80)
    print("Agent 1 will:")
    print("1. Research your goal thoroughly")
    print("2. Design optimal crew configuration")
    print("3. Build the crew per its specifications")
    print("4. Execute the crew with maximum verbosity")
    print("")
    
    try:
        # Get user goal
        goal = get_user_goal()
        
        # Agent 1 researches and designs crew
        agent1_result = run_agent1_research(goal)
        
        # Parse Agent 1's crew configuration
        config = parse_agent1_config(agent1_result)
        
        # Build crew per Agent 1's design
        crew = build_agent1_crew(config, goal)
        
        # Execute Agent 1's crew
        result = execute_agent1_crew(crew, config, goal)
        
        if result:
            print(f"\n🎉 COMPLETE SUCCESS!")
            print(f"✅ Agent 1 researched and analyzed the goal")
            print(f"✅ Agent 1 designed optimal crew configuration")
            print(f"✅ Crew was built per Agent 1's specifications")
            print(f"✅ Crew executed with maximum verbosity")
            print(f"📁 Check exported_results/ for complete work")
        else:
            print(f"\n❌ Execution failed")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()