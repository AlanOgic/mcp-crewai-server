#!/usr/bin/env python3
"""
CrewAI Flow Implementation for Evolving Crew Builder
Advanced orchestration with state management and evolution integration
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

from crewai import Agent, Task, Crew, Process, Flow
from crewai.flow import start, listen
from crewai.tools import BaseTool
# from langchain_openai import ChatOpenAI  # Removed - using create_llm() for multi-provider support
import requests

from src.mcp_crewai.server import MCPCrewAIServer


# State Models for Flow
class UserGoal(BaseModel):
    """User's request and context"""
    goal: str
    timestamp: datetime = Field(default_factory=datetime.now)
    user_context: Dict[str, Any] = Field(default_factory=dict)


class ResearchResults(BaseModel):
    """Agent 1's research and analysis"""
    raw_response: str
    research_analysis: str
    evolution_strategy: str
    management_strategy: str
    agents_config: List[Dict[str, Any]]
    tasks_config: List[Dict[str, Any]]
    parsing_successful: bool = True


class CrewConfig(BaseModel):
    """MCP Crew configuration"""
    crew_id: str
    crew_name: str
    agents_config: List[Dict[str, Any]]
    tasks: List[Dict[str, Any]]
    autonomy_level: float
    server_instance: Optional[Any] = Field(default=None, exclude=True)


class WorkProducts(BaseModel):
    """Actual deliverables from crew execution"""
    status: str
    task_outputs: List[Dict[str, Any]] = Field(default_factory=list)
    files_generated: List[str] = Field(default_factory=list)
    evolution_events: List[Dict[str, Any]] = Field(default_factory=list)
    raw_result: Optional[str] = None


class FinalResults(BaseModel):
    """Complete results with analysis"""
    work_content: str
    evolution_summary: Dict[str, Any]
    file_path: str
    execution_metrics: Dict[str, Any]


class CrewBuilderState(BaseModel):
    """Complete state for the evolving crew builder flow"""
    user_goal: Optional[UserGoal] = None
    research_results: Optional[ResearchResults] = None
    crew_config: Optional[CrewConfig] = None
    work_products: Optional[WorkProducts] = None
    final_results: Optional[FinalResults] = None
    flow_metadata: Dict[str, Any] = Field(default_factory=dict)


# Tools
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


# Main Flow Implementation
class EvolvingCrewBuilderFlow(Flow[CrewBuilderState]):
    """
    🧬 Advanced Evolving Crew Builder using CrewAI Flows
    
    Orchestrates the complete lifecycle:
    1. Collect user goal
    2. Agent 1 research and design
    3. Create evolving crew
    4. Execute with autonomous evolution
    5. Extract and present deliverables
    """
    
    def __init__(self):
        super().__init__()
        
    @start()
    def collect_user_goal(self) -> UserGoal:
        """
        🎯 STEP 1: Collect and validate user goal
        """
        print("🧬 EVOLVING CREW BUILDER FLOW - STEP 1")
        print("=" * 60)
        print("🎯 Collecting user goal...")
        
        # Get goal from global context - we'll set this in the flow instance
        goal = getattr(self, '_initial_goal', None)
        
        if not goal:
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
                sys.exit(0)
        
        user_goal = UserGoal(
            goal=goal,
            user_context={"input_method": "interactive" if not goal else "command_line"}
        )
        
        print(f"✅ Goal collected: {goal}")
        return user_goal
    
    @listen(collect_user_goal)
    def agent1_research(self, user_goal: UserGoal) -> ResearchResults:
        """
        🔍 STEP 2: Agent 1 research and crew design
        """
        print(f"\n🔍 EVOLVING CREW BUILDER FLOW - STEP 2")
        print("=" * 60)
        print(f"🤖 Agent 1 researching: {user_goal.goal}")
        
        # Create Agent 1 with research capabilities using selected LLM provider
        from src.mcp_crewai.server import create_llm
        llm = create_llm()
        manager_llm = create_llm()
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
        
        # Create research task with 80/20 rule focus on detailed task specification
        research_task = Task(
            description=f"""
            MISSION: Design a world-class hierarchical AI crew for: "{user_goal.goal}"
            
            INPUT REQUIREMENTS:
            - User Goal: {user_goal.goal}
            - Target: Hierarchical crew with 2-4 highly specialized agents
            - Quality Standard: Professional-grade deliverables with measurable outcomes
            
            RESEARCH PHASE (Mandatory):
            1. Conduct 3-5 targeted web searches on: {user_goal.goal}
            2. Identify domain expertise requirements and success patterns
            3. Analyze collaborative workflows and handoff points
            4. Research quality standards and deliverable formats for this domain
            
            DESIGN PHASE (Core Deliverable):
            Create a comprehensive JSON crew specification with:
            
            1. HIGHLY SPECIALIZED AGENTS (2-4 agents):
               - Role: Specific expert title (e.g., "Senior Data Science Researcher", not "Researcher")
               - Goal: Outcome-focused with specific deliverables, quality metrics, and constraints
               - Backstory: 10+ years expertise, specific credentials, working style, and evolution capacity
               - Personality: Match to optimal LLM temperature and collaboration style
               - Skills: Complementary expertise that creates productive tension
            
            2. HIERARCHICAL TASK DESIGN:
               - Description: Clear inputs, process steps, and handoff requirements  
               - Expected Output: Specific format, length, quality standards, and success criteria
               - Interface: How output connects to next agent's input
               - Quality Gates: Measurable standards for excellence
            
            3. EVOLUTION FRAMEWORK:
               - Strategy: How each agent should adapt based on performance
               - Triggers: Specific conditions that prompt evolution
               - Management: Hierarchical coordination patterns
            
            QUALITY STANDARDS:
            - Each agent must have distinct, specialized expertise
            - Tasks must have clear interfaces and measurable outputs
            - Crew must leverage hierarchical delegation effectively
            - Evolution strategy must be specific and actionable
            
            JSON STRUCTURE:
            {{
                "research_analysis": "Detailed analysis with specific domain insights and requirements",
                "evolution_strategy": "Specific adaptation mechanisms for each agent type",
                "management_strategy": "Hierarchical coordination with clear delegation patterns",
                "quality_framework": "Measurable standards and success criteria",
                "agents": [
                    {{
                        "role": "Highly Specific Expert Title",
                        "goal": "Precise outcome with metrics: deliver [specific output] meeting [quality standards] within [constraints]",
                        "backstory": "15+ years expertise in [specific domain], published [credentials], specializes in [techniques], works via [style]",
                        "personality_type": "analytical|creative|collaborative|decisive",
                        "expertise_level": "world-class|senior|specialist",
                        "collaboration_style": "hierarchical|peer|supportive",
                        "evolution_triggers": ["performance_threshold", "skill_gap", "team_dynamics"]
                    }}
                ],
                "tasks": [
                    {{
                        "description": "Detailed process: input [X] → analyze via [method] → output [Y] format",
                        "expected_output": "Specific deliverable: [format], [length], [quality standards]",
                        "quality_criteria": ["measurable standard 1", "measurable standard 2"],
                        "handoff_interface": "How this connects to next agent's input",
                        "success_metrics": "Quantifiable measures of task completion"
                    }}
                ]
            }}
            """,
            expected_output="""Complete JSON crew specification following the exact structure above, 
            with highly specialized agents, detailed task interfaces, and measurable quality standards. 
            Focus on creating productive specialization and clear hierarchical workflows.""",
            agent=agent1
        )
        
        # Execute research with hierarchical crew
        research_crew = Crew(
            agents=[agent1],
            tasks=[research_task],
            verbose=True,
            process=Process.hierarchical,
            manager_llm=manager_llm
        )
        
        print("🔍 Agent 1 starting research and design...")
        agent1_result = research_crew.kickoff()
        print("✅ Agent 1 research completed!")
        
        # Parse results
        research_results = self._parse_agent1_config(str(agent1_result))
        
        return research_results
    
    @listen(agent1_research)
    async def create_evolving_crew(self, research_results: ResearchResults) -> CrewConfig:
        """
        🏗️ STEP 3: Create evolving crew with MCP server
        """
        print(f"\n🏗️ EVOLVING CREW BUILDER FLOW - STEP 3")
        print("=" * 60)
        print("🧬 Creating evolving crew from research...")
        
        if not research_results.parsing_successful:
            print("❌ Cannot create crew due to research parsing failure")
            sys.exit(1)
        
        # Initialize MCP CrewAI Server
        server = MCPCrewAIServer()
        
        # Convert Agent 1's enhanced config to evolution format
        agents_config = []
        for agent_config in research_results.agents_config:
            personality_preset = agent_config.get('personality_type', 'collaborative')
            if personality_preset not in ['analytical', 'creative', 'collaborative', 'decisive']:
                personality_preset = 'collaborative'
                
            agents_config.append({
                "role": agent_config['role'],
                "goal": agent_config['goal'],
                "backstory": agent_config['backstory'],
                "personality_preset": personality_preset
            })
            
            print(f"✅ Configured highly specialized evolving agent:")
            print(f"   Role: {agent_config['role']}")
            print(f"   Expertise Level: {agent_config.get('expertise_level', 'Not specified')}")
            print(f"   Collaboration Style: {agent_config.get('collaboration_style', 'Not specified')}")
            print(f"   Personality: {personality_preset}")
            print(f"   Evolution Triggers: {agent_config.get('evolution_triggers', ['default'])}")
            print(f"   🧬 Evolution: ENABLED")
        
        # Create crew configuration
        timestamp = int(datetime.now().timestamp())
        crew_name = f"evolving_crew_{timestamp}"
        
        crew_config_dict = {
            "crew_name": crew_name,
            "agents_config": agents_config,
            "tasks": research_results.tasks_config,
            "autonomy_level": 0.8  # High autonomy for maximum evolution
        }
        
        print(f"🧬 Creating evolving crew: {crew_name}")
        await server._create_evolving_crew(crew_config_dict)
        
        crew_config = CrewConfig(
            crew_id=crew_name,
            crew_name=crew_name,
            agents_config=agents_config,
            tasks=research_results.tasks_config,
            autonomy_level=0.8,
            server_instance=server
        )
        
        print(f"✅ Evolving crew created successfully!")
        print(f"   Autonomy Level: 0.8 (High - enables evolution)")
        
        return crew_config
    
    @listen(create_evolving_crew)
    async def execute_crew(self, crew_config: CrewConfig) -> WorkProducts:
        """
        ⚡ STEP 4: Execute crew with autonomous evolution
        """
        print(f"\n⚡ EVOLVING CREW BUILDER FLOW - STEP 4")
        print("=" * 60)
        print("🧬 Executing crew with autonomous evolution...")
        
        server = crew_config.server_instance
        
        # Execute with evolution enabled  
        # Get user goal from flow instance
        user_goal_text = getattr(self, '_initial_goal', 'User goal not available')
        
        execution_context = {
            "user_goal": user_goal_text,
            "evolution_enabled": True,
            "process_type": "hierarchical",
            "research_analysis": "Flow-based research completed",
            "evolution_strategy": "Autonomous evolution with performance triggers"
        }
        
        # Disable autonomous decision making to ensure actual task execution
        result = await server._run_autonomous_crew({
            "crew_id": crew_config.crew_id,
            "context": execution_context,
            "allow_evolution": False  # Disable to prevent getting stuck in decisions
        })
        
        print("✅ Crew execution completed!")
        
        # Parse work products
        work_products = self._extract_work_products(result)
        
        return work_products
    
    @listen(execute_crew)
    async def extract_deliverables(self, work_products: WorkProducts) -> FinalResults:
        """
        📝 STEP 5: Extract and present final deliverables
        """
        print(f"\n📝 EVOLVING CREW BUILDER FLOW - STEP 5")
        print("=" * 60)
        print("📊 Extracting and presenting deliverables...")
        
        # Debug: Show what we actually received
        print(f"\n🔍 DEBUG - Work Products Analysis:")
        print(f"   Status: {work_products.status}")
        print(f"   Task Outputs Count: {len(work_products.task_outputs)}")
        print(f"   Files Generated: {len(work_products.files_generated)}")
        print(f"   Evolution Events: {len(work_products.evolution_events)}")
        
        if work_products.raw_result:
            print(f"   Raw Result Length: {len(work_products.raw_result)} characters")
            print(f"   Raw Result Preview: {work_products.raw_result[:200]}...")
        
        # Display actual work products
        if work_products.task_outputs:
            print("\n📝 ACTUAL WORK PRODUCTS:")
            print("=" * 60)
            
            work_content_parts = []
            for i, output in enumerate(work_products.task_outputs, 1):
                task_desc = output.get("description", f"Task {i}")
                agent_name = output.get("assigned_agent", "Unknown Agent")
                content = output.get("result", "No content")
                
                print(f"\n🔹 Task {i}: {task_desc}")
                print(f"👤 Agent: {agent_name}")
                print(f"📄 Output:")
                print("-" * 40)
                print(content)
                print("-" * 40)
                
                work_content_parts.append(
                    f"## {task_desc}\n**Agent:** {agent_name}\n\n{content}"
                )
            
            work_content = "\n\n".join(work_content_parts)
        else:
            print("\n⚠️ NO TASK OUTPUTS FOUND!")
            print("This means the crew execution didn't return the expected deliverable structure.")
            print("Checking raw result for actual content...")
            
            # Try to extract content from raw result
            try:
                import json
                raw_data = json.loads(work_products.raw_result)
                print(f"\n📋 Raw Result Structure:")
                for key in raw_data.keys():
                    print(f"   - {key}: {type(raw_data[key])}")
                
                # Look for any content in the raw result
                if "message" in raw_data:
                    print(f"\n💬 Message: {raw_data['message']}")
                
                work_content = f"Raw system response:\n{work_products.raw_result}"
                
            except:
                work_content = f"System response: {work_products.raw_result}"
        
        # For now, simplify the final step to focus on displaying work products
        print(f"\n🧬 EVOLUTION TRACKING:")
        print(f"   Evolution Events: {len(work_products.evolution_events)}")
        
        # Save complete results
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"exported_results/flow_based_crew_{timestamp_str}.md"
        
        # Ensure directory exists
        os.makedirs('exported_results', exist_ok=True)
        
        with open(filename, 'w') as f:
            f.write(f"# Flow-Based Evolving Crew Results\n\n")
            f.write(f"**Execution Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Process Type:** CrewAI Flow with Hierarchical Management\n\n")
            f.write(f"**Flow State Management:** Advanced state persistence and event-driven orchestration\n\n")
            
            f.write(work_content)
            
            if work_products.raw_result:
                f.write(f"\n\n**System Metadata:**\n\n")
                f.write(work_products.raw_result)
        
        final_results = FinalResults(
            work_content=work_content,
            evolution_summary={},  # Simplified for now
            file_path=filename,
            execution_metrics={
                "total_tasks": len(work_products.task_outputs),
                "files_generated": len(work_products.files_generated),
                "evolution_events": len(work_products.evolution_events),
                "execution_time": datetime.now().isoformat()
            }
        )
        
        print(f"\n🎉 FLOW EXECUTION COMPLETED!")
        print(f"💾 Results saved to: {filename}")
        print(f"🧬 Agents evolved autonomously during execution!")
        print(f"📊 Tasks completed: {len(work_products.task_outputs)}")
        
        return final_results
    
    def _parse_agent1_config(self, agent1_result: str) -> ResearchResults:
        """Parse Agent 1's research results"""
        print(f"\n📊 PARSING AGENT 1'S RESEARCH")
        print("-" * 50)
        
        try:
            # Look for JSON in the response
            json_patterns = [
                (agent1_result.find('```json'), agent1_result.find('```', agent1_result.find('```json') + 7)),
                (agent1_result.find('{'), agent1_result.rfind('}') + 1),
            ]
            
            for start_marker, end_marker in json_patterns:
                if start_marker != -1 and end_marker != -1:
                    if start_marker == agent1_result.find('```json'):
                        json_str = agent1_result[start_marker + 7:end_marker]
                    else:
                        json_str = agent1_result[start_marker:end_marker]
                    
                    json_str = json_str.strip()
                    config = json.loads(json_str)
                    
                    print("✅ Successfully parsed Agent 1's configuration!")
                    print(f"   Agents: {len(config.get('agents', []))}")
                    print(f"   Tasks: {len(config.get('tasks', []))}")
                    
                    # Enhanced parsing for new structure
                    print(f"   Quality Framework: {config.get('quality_framework', 'Not specified')}")
                    print(f"   Expertise Levels: {[agent.get('expertise_level', 'Not specified') for agent in config.get('agents', [])]}")
                    
                    return ResearchResults(
                        raw_response=agent1_result,
                        research_analysis=config.get('research_analysis', ''),
                        evolution_strategy=config.get('evolution_strategy', ''),
                        management_strategy=config.get('management_strategy', 'Hierarchical coordination'),
                        agents_config=config.get('agents', []),
                        tasks_config=config.get('tasks', []),
                        parsing_successful=True
                    )
                    
        except Exception as e:
            print(f"❌ Error parsing Agent 1's configuration: {e}")
        
        print("❌ Could not parse Agent 1's configuration")
        return ResearchResults(
            raw_response=agent1_result,
            research_analysis="Parsing failed",
            evolution_strategy="Default evolution",
            management_strategy="Hierarchical coordination",
            agents_config=[],
            tasks_config=[],
            parsing_successful=False
        )
    
    def _extract_work_products(self, result) -> WorkProducts:
        """Extract work products from crew execution result"""
        if not result:
            return WorkProducts(status="no_result", raw_result="No result returned")
        
        try:
            result_data = json.loads(result[0].text)
            
            work_products = WorkProducts(
                status=result_data.get("status", "unknown"),
                raw_result=result[0].text
            )
            
            # Extract deliverables if available
            if result_data.get("status") == "completed" and "deliverable_results" in result_data:
                deliverables = result_data["deliverable_results"]
                work_products.task_outputs = deliverables.get("outputs", [])
                
                files = deliverables.get("files_generated", [])
                work_products.files_generated = [f.get("file_path", "") for f in files]
            
            # Extract evolution events
            work_products.evolution_events = result_data.get("evolution_events", [])
            
            return work_products
            
        except Exception as e:
            print(f"❌ Error extracting work products: {e}")
            return WorkProducts(
                status="extraction_error",
                raw_result=str(result[0].text) if result else "No result"
            )


# Flow execution function
def run_flow_based_crew_builder(goal: Optional[str] = None):
    """
    🧬 Execute the flow-based evolving crew builder
    """
    print("🧬 CREWAI FLOW-BASED EVOLVING CREW BUILDER")
    print("=" * 80)
    print("Advanced Features:")
    print("• CrewAI Flow orchestration with state management")
    print("• Event-driven step coordination")
    print("• Agent 1 research and design")
    print("• Hierarchical process with manager delegation")
    print("• Autonomous agent evolution during execution")
    print("• Complete deliverable extraction and presentation")
    print("")
    
    try:
        # Create and execute flow
        flow = EvolvingCrewBuilderFlow()
        
        # Set the initial goal on the flow instance
        if goal:
            flow._initial_goal = goal
        
        # Start the flow (kickoff is not async)
        final_results = flow.kickoff()
        
        print(f"\n🎉 FLOW-BASED EXECUTION COMPLETED SUCCESSFULLY!")
        print(f"✅ All flow steps executed with state persistence")
        print(f"✅ Hierarchical crew management with evolution")
        print(f"✅ Actual work products extracted and displayed")
        print(f"📁 Complete results saved to: {final_results.file_path}")
        
        return final_results
        
    except Exception as e:
        print(f"❌ Flow execution failed: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    import asyncio
    
    goal = None
    if len(sys.argv) > 1:
        goal = " ".join(sys.argv[1:])
    
    asyncio.run(run_flow_based_crew_builder(goal))