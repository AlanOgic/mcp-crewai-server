#!/usr/bin/env python3
"""
GOAL → CREW → RESULTS
Simplest possible interface: Just provide your goal
"""

import asyncio
import json
import sys
from datetime import datetime
from mcp_crewai.server import MCPCrewAIServer

async def goal_to_results(goal: str):
    """Goal → Automatic crew → Real results"""
    
    print("🎯 GOAL TO CREW EXECUTION")
    print(f"Goal: {goal}")
    print()
    
    server = MCPCrewAIServer()
    
    # 1. Create intelligent crew
    print("🧠 Creating crew...")
    crew_result = await server._create_crew_from_project_analysis({
        "project_description": goal,
        "crew_name": f"goal_crew_{int(datetime.now().timestamp())}",
        "autonomy_level": 0.8
    })
    
    crew_data = json.loads(crew_result[0].text)
    crew_id = crew_data['crew_id']
    
    print(f"✅ Crew: {crew_id}")
    if 'crew_info' in crew_data:
        info = crew_data['crew_info']
        print(f"👥 {info.get('agents_count', 0)} agents, {info.get('tasks_count', 0)} tasks")
    
    # 2. Execute
    print("\n⚡ Executing...")
    await server._run_autonomous_crew({
        "crew_id": crew_id,
        "context": {"goal": goal},
        "allow_evolution": True
    })
    
    print("📊 Crew is working...")
    
    # 3. Wait for completion (simplified)
    import time
    await asyncio.sleep(60)  # Wait 1 minute for demonstration
    
    # 4. Get any available results
    print("\n📄 Getting results...")
    try:
        status_result = await server._get_crew_status({"crew_id": crew_id})
        status_data = json.loads(status_result[0].text)
        
        workflow_result = await server._get_workflow_status({"crew_id": crew_id})
        workflow_data = json.loads(workflow_result[0].text)
        
        # Save what we have
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"crew_output_{timestamp}.txt"
        
        with open(filename, 'w') as f:
            f.write(f"CREW EXECUTION RESULTS\n")
            f.write(f"Goal: {goal}\n")
            f.write(f"Crew ID: {crew_id}\n")
            f.write(f"Timestamp: {datetime.now()}\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Status: {status_data.get('overall_progress', 'In progress')}\n")
            f.write(f"Phase: {status_data.get('current_phase', 'Working')}\n\n")
            
            # Include any outputs
            if 'outputs' in workflow_data:
                f.write("OUTPUTS:\n")
                for name, content in workflow_data['outputs'].items():
                    f.write(f"\n{name}:\n{'-' * 40}\n{content}\n")
            
            if 'result' in workflow_data:
                f.write(f"\nRESULT:\n{'-' * 40}\n{workflow_data['result']}\n")
        
        print(f"💾 Results saved: {filename}")
        return filename
        
    except Exception as e:
        print(f"⚠️ Error getting results: {e}")
        return None

def main():
    """Simple main function"""
    
    # Get goal from command line or use default
    if len(sys.argv) > 1:
        goal = " ".join(sys.argv[1:])
    else:
        goal = "Create a project overview document"
        print(f"Using default goal: {goal}")
        print("(Usage: python goal_to_crew.py 'your goal here')")
    
    print(f"\n🚀 Starting execution for: {goal}\n")
    
    # Run async execution
    try:
        result = asyncio.run(goal_to_results(goal))
        if result:
            print(f"\n🎉 Done! Check: {result}")
        else:
            print("\n⚠️ Execution completed but no results file")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()