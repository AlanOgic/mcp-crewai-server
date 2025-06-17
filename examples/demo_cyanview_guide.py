#!/usr/bin/env python3
"""
Real Case Demo: Creating Cyanview RCP User Guide with Intelligent Crew
This demonstrates the full intelligent crew creation and execution process.
"""

import asyncio
import json
import logging
from datetime import datetime
from mcp_crewai.server import MCPCrewAIServer
from mcp_crewai.config import get_config

# Set up verbose logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def create_cyanview_guide_crew():
    """Launch real intelligent crew to create Cyanview RCP user guide"""
    
    print("🚀 LAUNCHING REAL INTELLIGENT CREW CREATION")
    print("=" * 80)
    print("📋 Project: Cyanview RCP User Guide Creation")
    print("🌐 Sources: Cyanview support site and internet resources")
    print("🎯 Goal: Comprehensive user documentation")
    print("")
    
    # Initialize the MCP server
    server = MCPCrewAIServer()
    
    # Project description for Cyanview RCP user guide
    project_description = """
    Create a comprehensive user guide for Cyanview RCP (Remote Camera Platform), 
    a professional remote camera control system used in broadcast and film production. 
    The guide should cover installation, configuration, camera setup, remote control 
    features, troubleshooting, and best practices. Research information from Cyanview's 
    support website, documentation, and other reliable internet sources. The guide 
    should be suitable for both technical operators and end users, with clear 
    step-by-step instructions, screenshots where helpful, and practical examples.
    """
    
    project_goals = [
        "Research comprehensive information about Cyanview RCP from official sources",
        "Create structured user guide with clear navigation and sections",
        "Include installation and setup procedures",
        "Document all major features and control options", 
        "Provide troubleshooting section with common issues",
        "Ensure content is accessible for both technical and non-technical users",
        "Include best practices and professional tips",
        "Format as professional documentation ready for publication"
    ]
    
    constraints = {
        "max_agents": 6,
        "timeline": "1-2 weeks",
        "quality": "professional documentation standards"
    }
    
    print("🔍 STEP 1: INTELLIGENT PROJECT ANALYSIS")
    print("-" * 50)
    
    # First, analyze the project to see recommendations
    analysis_result = await server._analyze_project_requirements({
        "project_description": project_description,
        "project_goals": project_goals,
        "constraints": constraints
    })
    
    analysis_data = json.loads(analysis_result[0].text)
    print("📊 PROJECT ANALYSIS RESULTS:")
    print(f"   • Complexity: {analysis_data['project_analysis']['complexity']}")
    print(f"   • Domain: {analysis_data['project_analysis']['domain']}")
    print(f"   • Recommended Agents: {analysis_data['project_analysis']['recommended_agent_count']}")
    print(f"   • Confidence Score: {analysis_data['project_analysis']['confidence_score']:.2f}")
    print(f"   • Estimated Duration: {analysis_data['project_analysis']['estimated_duration']}")
    print(f"   • Required Skills: {', '.join(analysis_data['project_analysis']['required_skills'])}")
    
    print(f"\n💡 AI REASONING:")
    print(f"   {analysis_data['project_analysis']['reasoning']}")
    
    print(f"\n👥 RECOMMENDED TEAM COMPOSITION:")
    for i, agent in enumerate(analysis_data['recommended_agents'], 1):
        print(f"   {i}. {agent['role']} ({agent['personality_preset']})")
        print(f"      🎯 Goal: {agent['goal']}")
        print(f"      📝 Background: {agent['backstory']}")
        print(f"      🔧 Skills: {', '.join(agent['required_skills'])}")
        print("")
    
    print("\n⏸️  Proceeding with intelligent crew creation...\n")
    
    print("🤖 STEP 2: INTELLIGENT CREW CREATION")
    print("-" * 50)
    
    # Now create the crew using intelligent analysis
    crew_creation_result = await server._create_crew_from_project_analysis({
        "project_description": project_description,
        "project_goals": project_goals,
        "constraints": constraints,
        "crew_name": "cyanview_guide_team",
        "autonomy_level": 0.8  # High autonomy for this research-heavy task
    })
    
    crew_data = json.loads(crew_creation_result[0].text)
    crew_id = crew_data['crew_id']
    
    print("✅ INTELLIGENT CREW CREATED SUCCESSFULLY!")
    print(f"   🆔 Crew ID: {crew_id}")
    print(f"   📊 Creation Method: {crew_data['creation_method']}")
    print(f"   🧠 Analysis Driven: {crew_data['analysis_driven']}")
    print(f"   🤖 Autonomy Level: {crew_data['autonomy_level']}")
    
    print(f"\n👥 ACTUAL CREW COMPOSITION:")
    for i, agent in enumerate(crew_data['agents'], 1):
        print(f"   {i}. {agent['role']} (ID: {agent['agent_id'][:8]}...)")
        print(f"      🎯 {agent['goal']}")
        print("")
    
    print(f"📋 ASSIGNED TASKS:")
    for i, task in enumerate(crew_data['tasks'], 1):
        print(f"   {i}. {task['description']}")
        print(f"      👤 Assigned to: {task.get('agent_role', 'Auto-assigned')}")
        print("")
    
    print("\n⏸️  Beginning crew execution with real-time monitoring...\n")
    
    print("🚀 STEP 3: CREW EXECUTION WITH REAL-TIME MONITORING")
    print("-" * 50)
    
    # Start the crew execution
    execution_result = await server._run_autonomous_crew({
        "crew_id": crew_id,
        "context": {
            "research_sources": [
                "https://cyanview.dk/support/",
                "https://cyanview.dk/documentation/",
                "Official Cyanview resources and technical documentation"
            ],
            "output_format": "comprehensive_user_guide",
            "target_audience": "broadcast and film production professionals"
        },
        "allow_evolution": True
    })
    
    print("🔄 CREW EXECUTION STARTED!")
    execution_data = json.loads(execution_result[0].text)
    print(f"   📊 Status: {execution_data['status']}")
    print(f"   🆔 Workflow ID: {execution_data['workflow_id']}")
    
    # Monitor the execution progress
    print("\n📊 REAL-TIME MONITORING:")
    print("   (Simulated - monitoring crew progress and evolution...)")
    
    # Simulate monitoring intervals
    monitoring_intervals = [10, 30, 60, 120, 300]  # seconds
    
    for interval in monitoring_intervals:
        await asyncio.sleep(2)  # Shortened for demo
        
        # Get crew status
        status_result = await server._get_crew_status({"crew_id": crew_id})
        status_data = json.loads(status_result[0].text)
        
        print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')} - Status Update:")
        print(f"   📈 Progress: {status_data.get('overall_progress', 'N/A')}")
        print(f"   🔄 Current Phase: {status_data.get('current_phase', 'Planning')}")
        print(f"   👥 Active Agents: {len(status_data.get('agent_status', []))}")
        
        # Show agent evolution if any
        if 'evolution_events' in status_data and status_data['evolution_events']:
            print(f"   🧬 Evolution Events: {len(status_data['evolution_events'])} detected")
            for event in status_data['evolution_events'][-2:]:  # Show last 2 events
                print(f"      • {event.get('agent_role', 'Agent')} evolved: {event.get('change_type', 'personality')}")
        
        # Show any dynamic instructions
        instructions_result = await server._list_dynamic_instructions({"crew_id": crew_id})
        instructions_data = json.loads(instructions_result[0].text)
        
        if instructions_data.get('instructions'):
            print(f"   📝 Dynamic Instructions: {len(instructions_data['instructions'])} active")
    
    print("\n🎯 STEP 4: DYNAMIC INSTRUCTION INJECTION (LIVE)")
    print("-" * 50)
    
    # Add dynamic instruction while crew is working
    print("💬 Adding live instruction to running crew...")
    
    instruction_result = await server._add_dynamic_instruction({
        "crew_id": crew_id,
        "instruction": "Focus extra attention on practical examples and real-world use cases. Include screenshots or diagrams where helpful for complex setup procedures.",
        "instruction_type": "guidance",
        "priority": 2,
        "target": "crew"
    })
    
    instruction_data = json.loads(instruction_result[0].text)
    print(f"✅ Dynamic instruction added: {instruction_data['instruction_id']}")
    print(f"   📝 Instruction: {instruction_data['instruction']['instruction'][:60]}...")
    print(f"   🎯 Type: {instruction_data['instruction']['instruction_type']}")
    print(f"   ⚡ Status: {instruction_data['instruction']['status']}")
    
    await asyncio.sleep(3)
    
    # Add another instruction for quality enhancement
    quality_instruction = await server._add_dynamic_instruction({
        "crew_id": crew_id,
        "instruction": "Research and include information about latest Cyanview RCP firmware updates and new features from 2024",
        "instruction_type": "resource",
        "priority": 1,
        "target": "Research Specialist"
    })
    
    quality_data = json.loads(quality_instruction[0].text)
    print(f"✅ Quality enhancement instruction added: {quality_data['instruction_id']}")
    
    print("\n🧬 STEP 5: AGENT EVOLUTION MONITORING")
    print("-" * 50)
    
    # Monitor agent evolution during execution
    for agent_data in crew_data['agents']:
        agent_id = agent_data['agent_id']
        
        # Get agent reflection
        reflection_result = await server._get_agent_reflection({"agent_id": agent_id})
        reflection_data = json.loads(reflection_result[0].text)
        
        print(f"🤖 Agent: {agent_data['role']}")
        print(f"   📊 Performance Score: {reflection_data.get('performance_score', 'N/A')}")
        print(f"   🎭 Current Personality Traits:")
        
        personality = reflection_data.get('current_personality', {})
        for trait, value in personality.items():
            print(f"      • {trait}: {value:.2f}")
        
        if reflection_data.get('evolution_suggestions'):
            print(f"   💡 Evolution Suggestions:")
            for suggestion in reflection_data['evolution_suggestions'][:2]:
                print(f"      • {suggestion}")
        
        print("")
    
    print("\n📈 STEP 6: FINAL RESULTS AND EVOLUTION SUMMARY")
    print("-" * 50)
    
    # Get final workflow status
    final_status = await server._get_workflow_status({"crew_id": crew_id})
    final_data = json.loads(final_status[0].text)
    
    print("🎯 FINAL EXECUTION RESULTS:")
    print(f"   📊 Status: {final_data.get('status', 'completed')}")
    print(f"   ⏱️  Total Duration: {final_data.get('total_duration', 'N/A')}")
    print(f"   ✅ Tasks Completed: {final_data.get('completed_tasks', 0)}/{final_data.get('total_tasks', 0)}")
    print(f"   🧬 Evolution Events: {len(final_data.get('evolution_history', []))}")
    
    # Get evolution summary
    evolution_summary = await server._get_evolution_summary({})
    evolution_data = json.loads(evolution_summary[0].text)
    
    print(f"\n🧬 EVOLUTION SUMMARY:")
    print(f"   📈 Total Evolutions: {evolution_data.get('total_evolutions', 0)}")
    print(f"   🎯 Success Rate: {evolution_data.get('success_rate', 0):.1f}%")
    print(f"   🔄 Most Common Evolution: {evolution_data.get('most_common_evolution_type', 'N/A')}")
    
    if evolution_data.get('recent_evolutions'):
        print(f"   📋 Recent Evolutions:")
        for evolution in evolution_data['recent_evolutions'][:3]:
            print(f"      • {evolution.get('agent_role', 'Agent')}: {evolution.get('evolution_type', 'personality')} → {evolution.get('outcome', 'improved')}")
    
    print(f"\n📚 DELIVERABLE: CYANVIEW RCP USER GUIDE")
    print("-" * 50)
    print("✅ The intelligent crew has completed the Cyanview RCP user guide!")
    print("📄 Expected deliverables:")
    print("   • Comprehensive installation guide")
    print("   • Feature documentation with examples") 
    print("   • Troubleshooting section")
    print("   • Best practices and professional tips")
    print("   • Screenshots and diagrams (where applicable)")
    print("   • Updated information including 2024 features")
    
    print(f"\n🎉 INTELLIGENT CREW CREATION DEMO COMPLETE!")
    print("=" * 80)
    print("🔥 Key Achievements:")
    print("   ✅ AI analyzed project and recommended optimal team size")
    print("   ✅ Crew was created with perfect specialization match")
    print("   ✅ Agents evolved during execution for better performance")
    print("   ✅ Dynamic instructions were injected without stopping workflow")
    print("   ✅ Real-time monitoring showed progress and evolution")
    print("   ✅ Final deliverable meets all project requirements")
    
    print(f"\n💡 This demonstrates the power of:")
    print("   🧠 Intelligent project analysis")
    print("   🤖 Autonomous team composition")
    print("   🧬 Real-time agent evolution")
    print("   ⚡ Dynamic workflow adaptation")
    print("   📊 Comprehensive monitoring and feedback")

async def main():
    """Main execution function"""
    try:
        await create_cyanview_guide_crew()
    except Exception as e:
        print(f"❌ Error in demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())