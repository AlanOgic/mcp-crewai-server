#!/usr/bin/env python3
"""
MCP CrewAI Server - Demo Usage Examples
"""

import json
import asyncio
from datetime import datetime

# This would be used via MCP client (Claude, n8n, etc.)
# Here we show what the calls would look like


async def demo_basic_crew_creation():
    """Demo: Create and run basic evolving crew"""
    
    print("🚀 DEMO: Creating Evolving Crew")
    print("=" * 50)
    
    # 1. Create evolving crew
    crew_config = {
        "crew_name": "content_marketing_team",
        "agents_config": [
            {
                "role": "Content Strategist",
                "goal": "Develop comprehensive content strategies that drive engagement",
                "backstory": "Expert in content planning with 5+ years experience in digital marketing",
                "personality_preset": "analytical"
            },
            {
                "role": "Creative Writer",
                "goal": "Create compelling and engaging content that resonates with audiences",
                "backstory": "Passionate storyteller with expertise in various content formats",
                "personality_preset": "creative"
            },
            {
                "role": "SEO Specialist",
                "goal": "Optimize content for maximum search visibility and organic reach",
                "backstory": "Data-driven SEO expert focused on technical and content optimization",
                "personality_preset": "analytical"
            }
        ],
        "tasks": [
            {
                "description": "Analyze target audience and develop content strategy for Q1 campaign",
                "agent_role": "Content Strategist"
            },
            {
                "description": "Create engaging blog posts and social media content based on strategy",
                "agent_role": "Creative Writer"
            },
            {
                "description": "Optimize all content for search engines and track performance",
                "agent_role": "SEO Specialist"
            }
        ],
        "autonomy_level": 0.7  # High autonomy
    }
    
    print("Creating crew with agents:")
    for agent in crew_config["agents_config"]:
        print(f"  - {agent['role']} ({agent['personality_preset']})")
    
    # This would be sent to MCP server
    print(f"\n📤 MCP Call: create_evolving_crew")
    print(f"📄 Config: {json.dumps(crew_config, indent=2)}")
    
    return crew_config


async def demo_dynamic_instructions():
    """Demo: Send dynamic instructions during execution"""
    
    print("\n🔄 DEMO: Dynamic Instructions During Execution")
    print("=" * 50)
    
    crew_id = "content_marketing_team"
    
    # Start crew execution (in background)
    print(f"🏃 Starting crew execution: {crew_id}")
    print("📤 MCP Call: run_autonomous_crew")
    
    # Simulate instructions sent during execution
    instructions = [
        {
            "instruction": "Focus on B2B audience - we just got intel they're our highest converters",
            "instruction_type": "guidance",
            "priority": 4,
            "delay": 2  # seconds into execution
        },
        {
            "instruction": "Budget increased by 40% - you can be more ambitious with content scope",
            "instruction_type": "resource",
            "priority": 3,
            "delay": 5
        },
        {
            "instruction": "CEO wants to see draft by 3 PM today - adjust timeline accordingly",
            "instruction_type": "constraint",
            "priority": 5,
            "delay": 8
        },
        {
            "instruction": "Boost creative thinking - the competition just launched something similar",
            "instruction_type": "skill_boost",
            "priority": 3,
            "delay": 12
        }
    ]
    
    for i, instr in enumerate(instructions):
        print(f"\n⏰ T+{instr['delay']}s: Sending dynamic instruction #{i+1}")
        print(f"📝 Type: {instr['instruction_type']}")
        print(f"💬 Message: {instr['instruction']}")
        
        mcp_call = {
            "tool": "add_dynamic_instruction",
            "arguments": {
                "crew_id": crew_id,
                "instruction": instr["instruction"],
                "instruction_type": instr["instruction_type"],
                "priority": instr["priority"]
            }
        }
        print(f"📤 MCP Call: {json.dumps(mcp_call, indent=2)}")


async def demo_mcp_client_integration():
    """Demo: Agents using external MCP servers as tools"""
    
    print("\n🔌 DEMO: MCP Client Integration")
    print("=" * 50)
    
    agent_id = "agent_001"  # From crew creation
    
    # 1. Connect to external MCP servers
    mcp_servers = [
        {
            "name": "github_mcp",
            "command": ["python", "-m", "github_mcp"],
            "description": "GitHub operations and repository management"
        },
        {
            "name": "notion_mcp", 
            "command": ["python", "-m", "notion_mcp"],
            "description": "Notion workspace and database management"
        },
        {
            "name": "weather_mcp",
            "command": ["python", "-m", "weather_mcp"], 
            "description": "Weather data and forecasting"
        }
    ]
    
    print("🔍 Auto-discovering MCP servers for agent...")
    discovery_call = {
        "tool": "auto_discover_mcp_servers",
        "arguments": {
            "agent_id": agent_id,
            "discovery_config": mcp_servers
        }
    }
    print(f"📤 MCP Call: {json.dumps(discovery_call, indent=2)}")
    
    # 2. Agent gets tool suggestions for task
    print(f"\n🤖 Agent suggesting tools for content creation task...")
    suggestion_call = {
        "tool": "suggest_tools_for_task",
        "arguments": {
            "agent_id": agent_id,
            "task_description": "Create a GitHub repository for our content marketing campaign and set up project tracking"
        }
    }
    print(f"📤 MCP Call: {json.dumps(suggestion_call, indent=2)}")
    
    # 3. Agent uses specific tool
    print(f"\n⚡ Agent using GitHub MCP tool...")
    tool_use_call = {
        "tool": "agent_use_mcp_tool",
        "arguments": {
            "agent_id": agent_id,
            "tool_name": "github_mcp::create_repository",
            "arguments": {
                "name": "content-marketing-q1",
                "description": "Q1 Content Marketing Campaign Assets",
                "private": False,
                "initialize": True
            },
            "context": "Setting up repository for content marketing campaign collaboration"
        }
    }
    print(f"📤 MCP Call: {json.dumps(tool_use_call, indent=2)}")


async def demo_agent_evolution():
    """Demo: Agent self-reflection and evolution"""
    
    print("\n🧬 DEMO: Agent Evolution and Self-Reflection")
    print("=" * 50)
    
    agent_id = "agent_002"  # Creative Writer from crew
    
    # 1. Get agent's self-reflection
    print("🧠 Agent performing self-reflection...")
    reflection_call = {
        "tool": "get_agent_reflection",
        "arguments": {
            "agent_id": agent_id
        }
    }
    print(f"📤 MCP Call: {json.dumps(reflection_call, indent=2)}")
    
    # Simulated reflection result
    reflection_result = {
        "agent_id": agent_id,
        "role": "Creative Writer",
        "self_reflection": {
            "performance_analysis": {
                "success_rate": 0.65,
                "efficiency": 0.8,
                "collaboration": 0.4  # Low collaboration!
            },
            "role_effectiveness": {
                "alignment_score": 0.7,
                "role_mismatch": 0.3
            },
            "skill_gaps": ["collaboration", "strategic_thinking"],
            "evolution_suggestions": {
                "personality_adjustments": {
                    "collaborative": 0.7,  # Increase from 0.4
                    "analytical": 0.6      # Gain some analytical skills
                },
                "skill_development": ["strategic_thinking"],
                "radical_changes": []
            }
        },
        "should_evolve": True,
        "evolution_readiness": "ready"
    }
    
    print(f"\n📊 Agent Reflection Results:")
    print(f"  - Success Rate: {reflection_result['self_reflection']['performance_analysis']['success_rate']}")
    print(f"  - Collaboration Score: {reflection_result['self_reflection']['performance_analysis']['collaboration']} (needs improvement!)")
    print(f"  - Evolution Needed: {reflection_result['should_evolve']}")
    
    # 2. Trigger evolution
    print(f"\n🔄 Triggering agent evolution...")
    evolution_call = {
        "tool": "trigger_agent_evolution",
        "arguments": {
            "agent_id": agent_id,
            "evolution_type": "personality"
        }
    }
    print(f"📤 MCP Call: {json.dumps(evolution_call, indent=2)}")
    
    # 3. Check evolution results
    print(f"\n✨ Post-evolution personality traits:")
    evolved_traits = {
        "analytical": 0.6,      # Increased from 0.4
        "creative": 0.9,        # Maintained strength
        "collaborative": 0.7,   # Significantly improved!
        "decisive": 0.6,
        "adaptable": 0.8,
        "risk_taking": 0.7
    }
    
    for trait, value in evolved_traits.items():
        print(f"  - {trait.title()}: {value}")
    
    print(f"\n🎉 Agent evolved! Now more collaborative and analytical while maintaining creativity.")


async def demo_crew_self_assessment():
    """Demo: Crew autonomous self-assessment"""
    
    print("\n🎯 DEMO: Crew Self-Assessment and Autonomous Decisions")
    print("=" * 50)
    
    crew_id = "content_marketing_team"
    
    # 1. Crew self-assessment
    print("🔍 Crew performing self-assessment...")
    assessment_call = {
        "tool": "crew_self_assessment",
        "arguments": {
            "crew_id": crew_id
        }
    }
    print(f"📤 MCP Call: {json.dumps(assessment_call, indent=2)}")
    
    # Simulated assessment result
    assessment_result = {
        "crew_id": crew_id,
        "self_assessment": {
            "skill_coverage": {
                "analytical": 0.8,
                "creative": 0.9,
                "collaborative": 0.6,
                "technical": 0.7
            },
            "resource_adequacy": {
                "tools": True,
                "knowledge": True,
                "data_access": True
            },
            "team_balance": 0.65,
            "missing_elements": [
                "agent_with_project_management_skills",
                "access_to_design_tools"
            ]
        },
        "improvement_suggestions": [
            "Add: agent_with_project_management_skills, access_to_design_tools",
            "Improve team personality diversity"
        ],
        "confidence_level": 0.65,
        "recommendation": "evolve"
    }
    
    print(f"\n📊 Self-Assessment Results:")
    print(f"  - Team Balance: {assessment_result['self_assessment']['team_balance']}")
    print(f"  - Confidence Level: {assessment_result['confidence_level']}")
    print(f"  - Missing Elements: {', '.join(assessment_result['self_assessment']['missing_elements'])}")
    print(f"  - Recommendation: {assessment_result['recommendation']}")
    
    # 2. Crew makes autonomous decision
    print(f"\n🧠 Crew making autonomous decision based on self-assessment...")
    
    autonomous_decision = {
        "action": "modify_team",
        "changes": [
            "add_agent_with_project_management_skills",
            "connect_to_design_tool_mcp_server"
        ],
        "reasoning": "Team lacks project management coordination and design capabilities for comprehensive content creation"
    }
    
    print(f"🎯 Autonomous Decision:")
    print(f"  - Action: {autonomous_decision['action']}")
    print(f"  - Reasoning: {autonomous_decision['reasoning']}")
    print(f"  - Changes: {', '.join(autonomous_decision['changes'])}")
    
    # 3. Execute autonomous changes
    print(f"\n⚡ Executing autonomous changes...")
    print(f"  ➕ Adding Project Manager agent...")
    print(f"  🔌 Connecting to Design Tools MCP server...")
    print(f"  🔄 Rebalancing team dynamics...")
    
    print(f"\n🎉 Crew evolved autonomously! Now has better project management and design capabilities.")


async def demo_real_world_scenario():
    """Demo: Complete real-world scenario"""
    
    print("\n🌍 DEMO: Complete Real-World Scenario")
    print("=" * 60)
    print("Scenario: Marketing team launching new product campaign")
    print("- Initial team struggles with coordination")  
    print("- Receives dynamic guidance during execution")
    print("- Agents evolve based on challenges faced")
    print("- Team autonomously adapts to new requirements")
    print("=" * 60)
    
    # Timeline of events
    timeline = [
        "🕐 00:00 - Crew created with basic personalities",
        "🕐 00:30 - Execution starts, agents working in silos", 
        "🕐 01:00 - User notices poor collaboration, sends guidance",
        "🕐 01:30 - Budget increase announced, resources provided",
        "🕐 02:00 - Competitor launches similar product, urgency instruction",
        "🕐 02:30 - Creative Writer evolves collaboration skills",
        "🕐 03:00 - Crew self-assesses, identifies missing PM skills",
        "🕐 03:30 - Crew autonomously adds Project Manager",
        "🕐 04:00 - Team connects to design tools via MCP",
        "🕐 04:30 - Successful campaign launch with evolved team",
    ]
    
    for event in timeline:
        print(event)
    
    print(f"\n🎯 Result: What started as a struggling team became a high-performing,")
    print(f"   self-evolving marketing crew capable of autonomous adaptation!")


async def main():
    """Run all demos"""
    await demo_basic_crew_creation()
    await demo_dynamic_instructions()
    await demo_mcp_client_integration()
    await demo_agent_evolution()
    await demo_crew_self_assessment()
    await demo_real_world_scenario()
    
    print(f"\n" + "=" * 70)
    print(f"🚀 MCP CrewAI Server - Revolutionary Autonomous Evolution Demo Complete!")
    print(f"🌟 This showcases the future of AI collaboration:")
    print(f"   • Agents that evolve their personalities over time")
    print(f"   • Dynamic instructions without stopping workflows")
    print(f"   • Universal MCP integration for unlimited tools")
    print(f"   • Autonomous crew self-assessment and adaptation")
    print(f"=" * 70)


if __name__ == "__main__":
    asyncio.run(main())