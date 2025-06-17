#!/usr/bin/env python3
"""
SIMPLE CREW INTERFACE - REAL OPERATIONS ONLY
Ask for goal → Create crew → Execute → Get results
"""

import asyncio
import json
import sys
import time
from datetime import datetime
from mcp_crewai.server import MCPCrewAIServer

async def simple_crew_execution(goal: str):
    """Simple: Goal → Real Crew → Real Results"""
    
    print("🚀 SIMPLE CREW EXECUTION")
    print("=" * 60)
    print(f"🎯 Goal: {goal}")
    print()
    
    server = MCPCrewAIServer()
    
    # Create crew with intelligent analysis
    print("🧠 Creating intelligent crew...")
    crew_result = await server._create_crew_from_project_analysis({
        "project_description": goal,
        "crew_name": f"simple_crew_{int(time.time())}",
        "autonomy_level": 0.8
    })
    
    crew_data = json.loads(crew_result[0].text)
    crew_id = crew_data['crew_id']
    crew_info = crew_data.get('crew_info', {})
    
    print(f"✅ Crew: {crew_id}")
    print(f"👥 Agents: {crew_info.get('agents_count', 0)}")
    print(f"📋 Tasks: {crew_info.get('tasks_count', 0)}")
    
    # Show project analysis
    if 'project_analysis' in crew_data:
        analysis = crew_data['project_analysis']
        print(f"🧠 Analysis: {analysis['complexity']} {analysis['domain']} project")
        print(f"⏱️ Duration: {analysis['estimated_duration']}")
        print(f"🔧 Skills: {', '.join(analysis['required_skills'])}")
    
    print()
    
    # Execute crew
    print("⚡ Executing crew...")
    execution_result = await server._run_autonomous_crew({
        "crew_id": crew_id,
        "context": {"goal": goal},
        "allow_evolution": True
    })
    
    execution_data = json.loads(execution_result[0].text)
    print(f"📊 Status: {execution_data.get('status', 'running')}")
    print()
    
    # Monitor execution 
    print("📈 Monitoring...")
    max_wait = 300  # 5 minutes
    start_time = time.time()
    
    while (time.time() - start_time) < max_wait:
        try:
            # Get status
            status_result = await server._get_crew_status({"crew_id": crew_id})
            status_data = json.loads(status_result[0].text)
            
            progress = status_data.get('overall_progress', '0%')
            phase = status_data.get('current_phase', 'working')
            
            print(f"📊 {progress} | {phase}")
            
            # Check workflow
            workflow_result = await server._get_workflow_status({"crew_id": crew_id})
            workflow_data = json.loads(workflow_result[0].text)
            
            if workflow_data.get('status') == 'completed':
                print("✅ Completed!")
                break
                
            if workflow_data.get('status') == 'failed':
                print("❌ Failed!")
                return None
                
        except Exception as e:
            print(f"⚠️ {str(e)[:50]}...")
        
        await asyncio.sleep(20)
    
    # Get final results
    print("\n📄 Getting results...")
    try:
        final_result = await server._get_workflow_status({"crew_id": crew_id})
        final_data = json.loads(final_result[0].text)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"result_{timestamp}.txt"
        
        with open(filename, 'w') as f:
            f.write(f"Goal: {goal}\n")
            f.write(f"Crew: {crew_id}\n")
            f.write(f"Completed: {datetime.now()}\n")
            f.write("=" * 60 + "\n\n")
            
            # Write outputs
            outputs = final_data.get('outputs', {})
            if outputs:
                for name, content in outputs.items():
                    f.write(f"{name}:\n{content}\n\n")
            else:
                result = final_data.get('result', 'No result available')
                f.write(str(result))
        
        print(f"💾 Saved: {filename}")
        
        # Show preview
        with open(filename, 'r') as f:
            content = f.read()
            preview = content[:300] + "..." if len(content) > 300 else content
        
        print(f"\n📖 PREVIEW:")
        print("-" * 40)
        print(preview)
        
        return filename
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

async def main():
    """Main execution"""
    
    print("🤖 SIMPLE CREW INTERFACE")
    print("Real operations only - no demos!")
    print("-" * 50)
    
    # Get goal
    if len(sys.argv) > 1:
        goal = " ".join(sys.argv[1:])
    else:
        goal = "Write a technical article about AI agent evolution in multi-agent systems"
        print(f"Using default goal: {goal}")
        print("(Custom: python simple_interface.py 'your goal')")
    
    print(f"\n🚀 Executing: {goal}")
    print()
    
    try:
        result_file = await simple_crew_execution(goal)
        
        if result_file:
            print(f"\n🎉 SUCCESS! Results in: {result_file}")
        else:
            print("\n❌ Execution failed")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())