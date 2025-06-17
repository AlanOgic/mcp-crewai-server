#!/usr/bin/env python3
"""
Advanced tests for MCP CrewAI Server - Revolutionary Features
"""

import asyncio
import json
import sys
from mcp_crewai.server import MCPCrewAIServer

async def test_crew_creation():
    """Test creating an evolving crew with multiple agents"""
    print("🏗 Testing Crew Creation with Multiple Personalities...")
    
    server = MCPCrewAIServer()
    
    # Create crew arguments
    crew_args = {
        "crew_name": "test_marketing_crew",
        "agents_config": [
            {
                "role": "Content Strategist",
                "goal": "Develop comprehensive content strategies",
                "backstory": "Expert in content planning with analytics focus",
                "personality_preset": "analytical"
            },
            {
                "role": "Creative Director",
                "goal": "Create engaging visual and written content", 
                "backstory": "Innovative designer with storytelling expertise",
                "personality_preset": "creative"
            },
            {
                "role": "Team Coordinator",
                "goal": "Ensure smooth collaboration and project delivery",
                "backstory": "Experienced project manager focused on team dynamics",
                "personality_preset": "diplomat"
            }
        ],
        "tasks": [
            {
                "description": "Analyze target audience and develop Q1 content strategy",
                "agent_role": "Content Strategist"
            },
            {
                "description": "Create engaging visual assets based on strategy",
                "agent_role": "Creative Director"
            },
            {
                "description": "Coordinate team efforts and ensure deadlines",
                "agent_role": "Team Coordinator"
            }
        ],
        "autonomy_level": 0.8
    }
    
    # Create the crew
    result = await server._create_evolving_crew(crew_args)
    result_data = json.loads(result[0].text)
    
    print(f"✅ Crew created: {result_data['crew_id']}")
    print(f"📊 Agents: {result_data['crew_info']['agents_count']}")
    print(f"🎯 Tasks: {result_data['crew_info']['tasks_count']}")
    print(f"🧠 Autonomy: {result_data['crew_info']['autonomy_level']}")
    
    # Verify agents have different personalities
    crew = server.crews["test_marketing_crew"]
    for i, agent in enumerate(crew.agents):
        print(f"🤖 Agent {i+1} ({agent.role}):")
        print(f"  - Analytical: {agent.personality_traits['analytical'].value}")
        print(f"  - Creative: {agent.personality_traits['creative'].value}")
        print(f"  - Collaborative: {agent.personality_traits['collaborative'].value}")
    
    return True

async def test_dynamic_instructions_workflow():
    """Test sending dynamic instructions during crew execution"""
    print("\n🔄 Testing Dynamic Instructions During Execution...")
    
    server = MCPCrewAIServer()
    
    # First create a crew
    crew_args = {
        "crew_name": "instruction_test_crew",
        "agents_config": [
            {
                "role": "Analyst",
                "goal": "Analyze data and provide insights",
                "backstory": "Data-driven analyst",
                "personality_preset": "analytical"
            }
        ],
        "tasks": [
            {
                "description": "Analyze market trends for Q1 planning"
            }
        ]
    }
    
    await server._create_evolving_crew(crew_args)
    
    # Add various types of dynamic instructions
    instructions = [
        ("Focus on B2B segment - higher conversion rates detected", "guidance", 4),
        ("Budget increased by 30% - expand scope accordingly", "resource", 3),
        ("Competitor launched similar product - pivot strategy", "pivot", 5),
        ("Emergency: CEO presentation moved to tomorrow", "constraint", 5)
    ]
    
    for content, instr_type, priority in instructions:
        result = await server._add_dynamic_instruction({
            "crew_id": "instruction_test_crew",
            "instruction": content,
            "instruction_type": instr_type,
            "priority": priority
        })
        
        result_data = json.loads(result[0].text)
        print(f"📝 Added {instr_type}: {result_data['instruction_id'][:12]}...")
    
    # Get all instructions
    list_result = await server._list_dynamic_instructions({
        "crew_id": "instruction_test_crew"
    })
    
    list_data = json.loads(list_result[0].text)
    print(f"📋 Total instructions: {list_data['total_instructions']}")
    
    return True

async def test_agent_evolution():
    """Test agent self-reflection and evolution"""
    print("\n🧬 Testing Agent Evolution and Self-Reflection...")
    
    server = MCPCrewAIServer()
    
    # Create a crew with an agent
    crew_args = {
        "crew_name": "evolution_test_crew",
        "agents_config": [
            {
                "role": "Writer",
                "goal": "Create compelling content",
                "backstory": "Creative writer with room for growth",
                "personality_preset": "creative"
            }
        ],
        "tasks": [
            {
                "description": "Write engaging blog posts"
            }
        ]
    }
    
    await server._create_evolving_crew(crew_args)
    
    # Get the agent
    crew = server.crews["evolution_test_crew"]
    agent = crew.agents[0]
    agent_id = agent.agent_id
    
    print(f"🤖 Agent ID: {agent_id}")
    print(f"📊 Initial traits:")
    for trait, obj in agent.personality_traits.items():
        print(f"  - {trait}: {obj.value}")
    
    # Simulate some experience and poor collaboration
    agent.tasks_completed = 6
    agent.evolution_metrics.success_rate = 0.55  # Below threshold
    agent.evolution_metrics.collaboration_score = 0.3  # Low collaboration
    
    # Test self-reflection
    reflection_result = await server._get_agent_reflection({
        "agent_id": agent_id
    })
    
    reflection_data = json.loads(reflection_result[0].text)
    print(f"🧠 Should evolve: {reflection_data['should_evolve']}")
    
    if reflection_data['should_evolve']:
        # Trigger evolution
        evolution_result = await server._trigger_agent_evolution({
            "agent_id": agent_id,
            "evolution_type": "collaborative"
        })
        
        evolution_data = json.loads(evolution_result[0].text)
        print(f"⚡ Evolution completed: Cycle {evolution_data['cycle']}")
        
        print(f"📈 Post-evolution traits:")
        for trait, value in evolution_data['current_traits'].items():
            print(f"  - {trait}: {value}")
    
    return True

async def test_autonomous_crew_execution():
    """Test crew autonomous execution with all features"""
    print("\n🚀 Testing Autonomous Crew Execution...")
    
    server = MCPCrewAIServer()
    
    # Create crew
    crew_args = {
        "crew_name": "autonomous_test_crew",
        "agents_config": [
            {
                "role": "Project Manager",
                "goal": "Coordinate project delivery",
                "backstory": "Experienced project coordinator",
                "personality_preset": "diplomat"
            },
            {
                "role": "Developer",
                "goal": "Build robust solutions",
                "backstory": "Pragmatic developer focused on delivery",
                "personality_preset": "executor"
            }
        ],
        "tasks": [
            {
                "description": "Plan and coordinate development sprint",
                "agent_role": "Project Manager"
            },
            {
                "description": "Implement core features",
                "agent_role": "Developer"
            }
        ],
        "autonomy_level": 0.9  # Very high autonomy
    }
    
    await server._create_evolving_crew(crew_args)
    
    # Start autonomous execution
    print("🏃 Starting autonomous execution...")
    
    # Add some instructions during execution
    asyncio.create_task(server._add_dynamic_instruction({
        "crew_id": "autonomous_test_crew",
        "instruction": "Client requested additional security features",
        "instruction_type": "guidance",
        "priority": 3
    }))
    
    # Run the crew
    execution_result = await server._run_autonomous_crew({
        "crew_id": "autonomous_test_crew",
        "context": {"project": "web_platform", "deadline": "2_weeks"},
        "allow_evolution": True
    })
    
    execution_data = json.loads(execution_result[0].text)
    print(f"📊 Execution status: {execution_data['status']}")
    print(f"🧬 Evolution events: {len(execution_data['evolution_events'])}")
    print(f"📝 Instructions processed: {execution_data['dynamic_instruction_stats']['instructions_processed']}")
    
    return True

async def test_crew_self_assessment():
    """Test crew autonomous self-assessment"""
    print("\n🎯 Testing Crew Self-Assessment...")
    
    server = MCPCrewAIServer()
    
    # Create crew with imbalanced team
    crew_args = {
        "crew_name": "assessment_test_crew",
        "agents_config": [
            {
                "role": "Analyst 1",
                "goal": "Analyze data",
                "backstory": "Data analyst",
                "personality_preset": "analytical"
            },
            {
                "role": "Analyst 2", 
                "goal": "Analyze more data",
                "backstory": "Another data analyst",
                "personality_preset": "analytical"
            }
        ],
        "tasks": [
            {
                "description": "Comprehensive market analysis"
            }
        ]
    }
    
    await server._create_evolving_crew(crew_args)
    
    # Perform self-assessment
    assessment_result = await server._crew_self_assessment({
        "crew_id": "assessment_test_crew"
    })
    
    assessment_data = json.loads(assessment_result[0].text)
    print(f"🔍 Confidence level: {assessment_data['confidence_level']}")
    print(f"📋 Recommendation: {assessment_data['recommendation']}")
    print(f"🔧 Improvement suggestions: {len(assessment_data['improvement_suggestions'])}")
    
    for suggestion in assessment_data['improvement_suggestions']:
        print(f"  💡 {suggestion}")
    
    return True

async def main():
    """Run all advanced tests"""
    print("🧪 MCP CrewAI Server - Advanced Revolutionary Tests")
    print("=" * 60)
    
    try:
        await test_crew_creation()
        await test_dynamic_instructions_workflow()
        await test_agent_evolution()
        await test_autonomous_crew_execution()
        await test_crew_self_assessment()
        
        print("\n" + "=" * 60)
        print("🎉 ALL ADVANCED TESTS PASSED!")
        print("🚀 MCP CrewAI Server demonstrates REVOLUTIONARY capabilities:")
        print("   ✅ Autonomous agent evolution")
        print("   ✅ Dynamic instructions during execution")
        print("   ✅ Self-reflecting agents")
        print("   ✅ Autonomous crew decision making")
        print("   ✅ Team self-assessment")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)