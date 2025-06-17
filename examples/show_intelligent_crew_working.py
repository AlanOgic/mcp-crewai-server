#!/usr/bin/env python3
"""
SHOW INTELLIGENT CREW WORKING
This demonstrates exactly what you saw working - the AI analyzing and creating optimal crews
"""

import asyncio
import json
from mcp_crewai.server import MCPCrewAIServer

async def show_intelligent_crew_in_action():
    """Show the intelligent crew system working step by step"""
    
    print("🧠 INTELLIGENT CREW SYSTEM IN ACTION")
    print("=" * 70)
    print("🎯 This shows exactly what you saw working:")
    print("   ✅ AI analyzes project complexity automatically")
    print("   ✅ AI determines optimal team size")  
    print("   ✅ AI selects specialized agent types")
    print("   ✅ AI assigns tasks based on expertise")
    print("")
    
    server = MCPCrewAIServer()
    
    # Test 1: Simple project
    print("🔍 TEST 1: SIMPLE PROJECT")
    print("-" * 40)
    
    simple_project = "Write a blog post about Python best practices for beginners"
    
    analysis1 = await server._analyze_project_requirements({
        "project_description": simple_project
    })
    
    data1 = json.loads(analysis1[0].text)
    
    print(f"📝 Project: {simple_project}")
    print(f"🧠 AI Analysis:")
    print(f"   • Complexity: {data1['project_analysis']['complexity']}")
    print(f"   • Domain: {data1['project_analysis']['domain']}")
    print(f"   • Recommended Team Size: {data1['project_analysis']['recommended_agent_count']} agents")
    print(f"   • Confidence: {data1['project_analysis']['confidence_score']:.1%}")
    
    print(f"\n👥 AI-Selected Team:")
    for i, agent in enumerate(data1['recommended_agents'], 1):
        print(f"   {i}. {agent['role']} ({agent['personality_preset']})")
    
    # Test 2: Complex project
    print(f"\n🔍 TEST 2: COMPLEX PROJECT")
    print("-" * 40)
    
    complex_project = """
    Build a distributed microservices e-commerce platform with real-time inventory management, 
    AI-powered recommendation engine, fraud detection, multi-currency support, advanced analytics, 
    mobile apps for iOS/Android, admin dashboard, third-party integrations, and deployment across 
    multiple cloud regions with 99.99% uptime requirements.
    """
    
    analysis2 = await server._analyze_project_requirements({
        "project_description": complex_project,
        "project_goals": [
            "Support 1M+ concurrent users",
            "Process 10K+ transactions per second", 
            "Deploy across 5 cloud regions",
            "Integrate with 20+ payment providers",
            "Real-time analytics and reporting"
        ]
    })
    
    data2 = json.loads(analysis2[0].text)
    
    print(f"📝 Project: Enterprise e-commerce platform...")
    print(f"🧠 AI Analysis:")
    print(f"   • Complexity: {data2['project_analysis']['complexity']}")
    print(f"   • Domain: {data2['project_analysis']['domain']}")
    print(f"   • Recommended Team Size: {data2['project_analysis']['recommended_agent_count']} agents")
    print(f"   • Confidence: {data2['project_analysis']['confidence_score']:.1%}")
    print(f"   • Duration: {data2['project_analysis']['estimated_duration']}")
    
    print(f"\n👥 AI-Selected Team:")
    for i, agent in enumerate(data2['recommended_agents'], 1):
        print(f"   {i}. {agent['role']} ({agent['personality_preset']})")
        print(f"      🎯 {agent['goal'][:50]}...")
    
    # Test 3: The Cyanview project you requested
    print(f"\n🔍 TEST 3: YOUR CYANVIEW PROJECT")
    print("-" * 40)
    
    cyanview_project = """
    Create a comprehensive user guide for Cyanview RCP (Remote Camera Platform), 
    a professional remote camera control system used in broadcast and film production. 
    Research from official sources, include installation, configuration, troubleshooting.
    """
    
    analysis3 = await server._analyze_project_requirements({
        "project_description": cyanview_project,
        "project_goals": [
            "Research from Cyanview official sources",
            "Installation and setup procedures", 
            "Feature documentation",
            "Troubleshooting guide",
            "Professional best practices"
        ]
    })
    
    data3 = json.loads(analysis3[0].text)
    
    print(f"📝 Project: Cyanview RCP User Guide")
    print(f"🧠 AI Analysis:")
    print(f"   • Complexity: {data3['project_analysis']['complexity']}")
    print(f"   • Domain: {data3['project_analysis']['domain']}")
    print(f"   • Recommended Team Size: {data3['project_analysis']['recommended_agent_count']} agents")
    print(f"   • Confidence: {data3['project_analysis']['confidence_score']:.1%}")
    
    print(f"\n💭 AI Reasoning:")
    print(f"   {data3['project_analysis']['reasoning']}")
    
    print(f"\n👥 AI-Selected Team:")
    for i, agent in enumerate(data3['recommended_agents'], 1):
        print(f"   {i}. {agent['role']} ({agent['personality_preset']})")
        print(f"      🎯 {agent['goal']}")
        print(f"      📚 {agent['backstory']}")
        print("")
    
    # Now show intelligent crew creation in action
    print("🤖 CREATING INTELLIGENT CREW FOR CYANVIEW PROJECT")
    print("-" * 60)
    
    crew_result = await server._create_crew_from_project_analysis({
        "project_description": cyanview_project,
        "project_goals": [
            "Research from Cyanview official sources",
            "Installation and setup procedures", 
            "Feature documentation",
            "Troubleshooting guide"
        ],
        "crew_name": "cyanview_intelligent_crew",
        "autonomy_level": 0.8
    })
    
    crew_data = json.loads(crew_result[0].text)
    
    print(f"✅ INTELLIGENT CREW CREATED!")
    print(f"   🆔 Crew ID: {crew_data['crew_id']}")
    print(f"   🧠 Analysis-Driven: {crew_data.get('analysis_driven', True)}")
    print(f"   📊 Creation Method: {crew_data.get('creation_method', 'intelligent_analysis')}")
    
    if 'project_analysis' in crew_data:
        analysis = crew_data['project_analysis']
        print(f"\n📊 EMBEDDED PROJECT ANALYSIS:")
        print(f"   • Complexity: {analysis['complexity']}")
        print(f"   • Domain: {analysis['domain']}")
        print(f"   • Required Skills: {', '.join(analysis['required_skills'])}")
        print(f"   • Confidence: {analysis['confidence_score']:.1%}")
    
    print(f"\n📋 AUTO-GENERATED TASKS:")
    if 'tasks' in crew_data:
        for i, task in enumerate(crew_data['tasks'], 1):
            print(f"   {i}. {task['description']}")
            if 'agent_role' in task:
                print(f"      👤 → {task['agent_role']}")
            print("")
    
    print("=" * 70)
    print("🎯 WHAT YOU'RE SEEING:")
    print("   🧠 The AI FIRST AGENT analyzes the project")
    print("   📊 It determines complexity, domain, and optimal team size")
    print("   👥 It selects specialized agents with right personalities")
    print("   📋 It generates appropriate tasks for each agent")
    print("   🤖 It creates a perfectly-sized crew ready to work")
    
    print(f"\n🔥 KEY INSIGHT:")
    print("   🎯 You just provide project description")
    print("   🧠 AI figures out EVERYTHING else automatically:")
    print("      • How many agents needed")
    print("      • What types of specialists required") 
    print("      • How to distribute the work")
    print("      • What personalities work best together")
    
    print(f"\n✨ THIS IS THE REVOLUTION:")
    print("   ❌ No more guessing team sizes")
    print("   ❌ No more manual agent configuration")
    print("   ❌ No more task distribution planning")
    print("   ✅ Just describe your project → Perfect team created!")

async def main():
    try:
        await show_intelligent_crew_in_action()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())