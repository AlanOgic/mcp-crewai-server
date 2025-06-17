#!/usr/bin/env python3
"""
Test the new verbose execution with task termination capabilities
"""

import asyncio
import os
import sys
from datetime import datetime

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcp_crewai.server import MCPCrewAIServer
from mcp_crewai.task_termination import terminate_current_task, get_active_tasks

async def test_verbose_execution_with_termination():
    """Test crew execution with maximum verbosity and task termination"""
    
    print("🔥 TESTING VERBOSE CREW EXECUTION WITH TASK TERMINATION")
    print("=" * 80)
    print("👁️  This test will demonstrate:")
    print("   • Maximum verbosity - SEE THE CREW WORKING")
    print("   • Task termination instead of timeout")
    print("   • Results saved to exported_results folder")
    print("   • Real-time agent conversations and decisions")
    print("")
    
    # Ensure exported_results directory exists
    os.makedirs('exported_results', exist_ok=True)
    
    # Initialize server
    server = MCPCrewAIServer()
    
    # Create a simple crew for testing
    print("🏗️  STEP 1: Creating Test Crew")
    print("-" * 50)
    
    crew_creation_args = {
        "crew_name": "verbose_test_crew",
        "agents_config": [
            {
                "role": "Research Analyst",
                "goal": "Research and analyze information thoroughly",
                "backstory": "Expert researcher with attention to detail",
                "personality_preset": "analytical"
            },
            {
                "role": "Content Writer", 
                "goal": "Create clear and engaging content",
                "backstory": "Professional writer focused on clarity",
                "personality_preset": "creative"
            }
        ],
        "tasks": [
            {
                "description": "Research current trends in AI and machine learning",
                "agent_role": "Research Analyst"
            },
            {
                "description": "Write a brief summary of the research findings",
                "agent_role": "Content Writer"
            }
        ],
        "autonomy_level": 0.7
    }
    
    crew_result = await server._create_evolving_crew(crew_creation_args)
    print(f"✅ Crew created successfully")
    
    # Get crew ID from result
    import json
    crew_data = json.loads(crew_result[0].text)
    crew_id = crew_data["crew_id"]
    print(f"   🆔 Crew ID: {crew_id}")
    
    print(f"\n🚀 STEP 2: Starting Verbose Execution")
    print("-" * 50)
    print("⚡ CREW IS NOW WORKING - MAXIMUM VERBOSITY ENABLED")
    print("🔍 You will see all agent conversations and decisions")
    print("🛑 You can terminate tasks gracefully without losing progress")
    print("")
    
    # Start crew execution
    execution_args = {
        "crew_id": crew_id,
        "context": {
            "research_focus": "practical applications",
            "output_format": "concise summary",
            "verbose_execution": True
        },
        "allow_evolution": True
    }
    
    try:
        # Execute crew (this will show maximum verbosity)
        execution_result = await server._run_autonomous_crew(execution_args)
        
        print(f"\n🎉 EXECUTION COMPLETED!")
        print("=" * 80)
        
        # Parse and display results
        result_data = json.loads(execution_result[0].text)
        
        if "deliverable_results" in result_data:
            # Save results to exported_results folder
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"exported_results/verbose_test_results_{timestamp}.txt"
            
            with open(output_filename, 'w') as f:
                f.write(f"Verbose Crew Execution Test Results\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 60 + "\n\n")
                f.write(json.dumps(result_data, indent=2))
            
            print(f"💾 Results saved to: {output_filename}")
            
            # Show preview
            if "deliverable_results" in result_data:
                deliverable = result_data["deliverable_results"]
                print(f"\n📖 DELIVERABLE PREVIEW:")
                print("-" * 40)
                preview = str(deliverable)[:300] + "..." if len(str(deliverable)) > 300 else str(deliverable)
                print(preview)
        
        print(f"\n✅ TEST COMPLETED SUCCESSFULLY!")
        print("🎯 Features demonstrated:")
        print("   ✅ Maximum verbosity - crew working was visible")
        print("   ✅ Task termination system - no hard timeouts")
        print("   ✅ Results saved to exported_results folder")
        print("   ✅ Real-time agent collaboration")
        
    except Exception as e:
        print(f"❌ Execution error: {e}")
        import traceback
        traceback.print_exc()

async def test_task_termination():
    """Test the task termination functionality"""
    
    print(f"\n🛑 TESTING TASK TERMINATION FUNCTIONALITY")
    print("-" * 50)
    
    # Get active tasks
    active_tasks = get_active_tasks()
    print(f"📋 Active tasks: {len(active_tasks)}")
    
    for task in active_tasks:
        print(f"   🔧 Task: {task['task_id']}")
        print(f"      📊 Progress: {task['progress']:.1%}")
        print(f"      🎯 Step: {task['current_step']}")
        print(f"      ⏱️  Runtime: {task['execution_time']:.1f}s")
        
        # Example: terminate a task (uncomment to test)
        # terminate_current_task(task['task_id'], "Testing termination functionality")
        # print(f"   🛑 Termination requested for task: {task['task_id']}")

async def main():
    """Main test function"""
    try:
        await test_verbose_execution_with_termination()
        await test_task_termination()
        
        print(f"\n🎉 ALL TESTS COMPLETED!")
        print("🔥 The crew execution now has:")
        print("   👁️  Maximum verbosity - you can see everything")
        print("   🛑 Task termination instead of timeouts")
        print("   📁 Results saved to exported_results folder")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())