#!/usr/bin/env python3
"""
SIMPLE CREW INTERFACE
Just provide a goal → Get real results automatically
"""

import asyncio
import json
import logging
import sys
import time
from datetime import datetime
from mcp_crewai.server import MCPCrewAIServer

# Maximum verbose logging to see everything
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f'simple_crew_verbose_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)

# Enable all loggers for maximum verbosity
loggers = [
    'mcp_crewai.server',
    'mcp_crewai.project_analyzer', 
    'mcp_crewai.evolution',
    'mcp_crewai.dynamic_instructions',
    'mcp_crewai.monitoring',
    'crewai'
]

for logger_name in loggers:
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)

async def create_and_run_crew(goal: str):
    """
    Simple interface: Goal → Automatic crew creation → Real execution → Results
    """
    
    print("🚀 SIMPLE CREW INTERFACE")
    print("=" * 60)
    print(f"🎯 Goal: {goal}")
    print("⚡ Creating intelligent crew automatically...")
    print()
    
    # Initialize server
    server = MCPCrewAIServer()
    
    # Step 1: Intelligent analysis and crew creation
    print("🧠 Step 1: AI analyzing project and creating optimal crew...")
    logger.info(f"Starting project analysis for goal: {goal}")
    
    crew_result = await server._create_crew_from_project_analysis({
        "project_description": goal,
        "crew_name": f"auto_crew_{int(time.time())}",
        "autonomy_level": 0.8
    })
    
    crew_data = json.loads(crew_result[0].text)
    logger.info(f"Crew creation response: {crew_data}")
    
    crew_id = crew_data['crew_id']
    
    # Get agent and task info from different possible structures
    agents = crew_data.get('agent_configs', crew_data.get('agents', []))
    tasks = crew_data.get('tasks', [])
    
    print(f"✅ Crew created: {crew_id}")
    print(f"👥 Team size: {len(agents)} agents")
    print(f"📋 Tasks: {len(tasks)}")
    
    # Show detailed agent info in verbose mode
    if agents:
        print("\n👥 AGENT DETAILS:")
        for i, agent in enumerate(agents, 1):
            role = agent.get('role', 'Unknown Role')
            goal = agent.get('goal', 'No goal specified')
            personality = agent.get('personality_preset', 'balanced')
            print(f"   {i}. {role}")
            print(f"      🎯 {goal}")
            print(f"      🎭 Personality: {personality}")
    else:
        print("⚠️ No agents found in crew data!")
        logger.warning(f"No agents in crew data. Available keys: {list(crew_data.keys())}")
    
    if tasks:
        print("\n📋 TASK BREAKDOWN:")
        for i, task in enumerate(tasks, 1):
            description = task.get('description', 'No description')
            print(f"   {i}. {description[:80]}...")
            assigned_to = task.get('agent_role', 'Auto-assigned')
            print(f"      👤 → {assigned_to}")
    else:
        print("⚠️ No tasks found in crew data!")
        logger.warning(f"No tasks in crew data. Available keys: {list(crew_data.keys())}")
    
    print()
    
    # Step 2: Execute crew
    print("🚀 Step 2: Running crew autonomously...")
    
    execution_result = await server._run_autonomous_crew({
        "crew_id": crew_id,
        "context": {
            "goal": goal,
            "execution_mode": "autonomous",
            "output_format": "comprehensive"
        },
        "allow_evolution": True
    })
    
    execution_data = json.loads(execution_result[0].text)
    logger.info(f"Execution response: {execution_data}")
    
    # Handle different response formats
    workflow_id = execution_data.get('workflow_id', execution_data.get('execution_id', crew_id))
    execution_status = execution_data.get('status', 'started')
    
    print(f"⚡ Execution started: {workflow_id}")
    print(f"📊 Status: {execution_status}")
    print("📊 Monitoring progress...")
    print()
    
    # Step 3: Monitor until completion
    print("📈 Step 3: Real-time monitoring with verbose updates...")
    
    max_wait_time = 600  # 10 minutes max
    start_time = time.time()
    last_status = None
    
    while (time.time() - start_time) < max_wait_time:
        try:
            # Check status with verbose details
            status_result = await server._get_crew_status({"crew_id": crew_id})
            status_data = json.loads(status_result[0].text)
            
            overall_progress = status_data.get('overall_progress', '0%')
            current_phase = status_data.get('current_phase', 'working')
            
            # Show detailed status if changed
            current_status = f"{overall_progress}|{current_phase}"
            if current_status != last_status:
                print(f"📊 Progress: {overall_progress} | Phase: {current_phase}")
                
                # Show agent status if available
                if 'agent_status' in status_data:
                    print("   🤖 Agent Status:")
                    for agent in status_data['agent_status']:
                        agent_role = agent.get('role', 'Unknown')
                        agent_status = agent.get('status', 'unknown')
                        current_task = agent.get('current_task', 'idle')[:50]
                        print(f"      • {agent_role}: {agent_status} - {current_task}...")
                
                # Show evolution events
                if 'evolution_events' in status_data and status_data['evolution_events']:
                    print("   🧬 Evolution Events:")
                    for event in status_data['evolution_events']:
                        print(f"      • {event.get('agent_role', 'Agent')}: {event.get('evolution_type', 'adaptation')}")
                
                last_status = current_status
            
            # Check workflow completion
            workflow_result = await server._get_workflow_status({"crew_id": crew_id})
            workflow_data = json.loads(workflow_result[0].text)
            
            if workflow_data.get('status') == 'completed':
                print("✅ Execution completed!")
                break
                
            if workflow_data.get('status') == 'failed':
                print("❌ Execution failed!")
                return None
            
            # Show detailed progress if available
            if 'progress_details' in workflow_data:
                progress = workflow_data['progress_details']
                completed = progress.get('completed_tasks', 0)
                total = progress.get('total_tasks', 1)
                if total > 0:
                    completion_pct = (completed / total) * 100
                    print(f"      📈 Tasks: {completed}/{total} ({completion_pct:.1f}%)")
                
        except Exception as e:
            logger.error(f"Monitoring error: {e}")
            print(f"⚠️ Monitoring error: {str(e)[:50]}...")
        
        await asyncio.sleep(15)  # Check every 15 seconds
    
    # Step 4: Get results
    print("\n📄 Step 4: Retrieving results...")
    
    try:
        final_status = await server._get_workflow_status({"crew_id": crew_id})
        final_data = json.loads(final_status[0].text)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = f"crew_result_{timestamp}.txt"
        
        with open(result_file, 'w') as f:
            f.write(f"Crew Execution Results\n")
            f.write(f"Goal: {goal}\n")
            f.write(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Crew ID: {crew_id}\n")
            f.write("=" * 60 + "\n\n")
            
            # Write all outputs
            if 'outputs' in final_data:
                for output_name, content in final_data['outputs'].items():
                    f.write(f"OUTPUT: {output_name}\n")
                    f.write("-" * 40 + "\n")
                    f.write(str(content))
                    f.write("\n\n")
            else:
                # Get the main result
                result_content = final_data.get('result', final_data.get('final_output', 'No output available'))
                f.write(str(result_content))
        
        print(f"💾 Results saved: {result_file}")
        
        # Show preview
        with open(result_file, 'r') as f:
            content = f.read()
            preview = content[:500] + "..." if len(content) > 500 else content
            
        print(f"\n📖 PREVIEW:")
        print("-" * 50)
        print(preview)
        
        if len(content) > 500:
            print(f"\n... and {len(content) - 500} more characters in {result_file}")
        
        print(f"\n🎉 SUCCESS!")
        print(f"🎯 Goal achieved: {goal}")
        print(f"📁 Full results: {result_file}")
        
        return result_file
        
    except Exception as e:
        print(f"❌ Error retrieving results: {e}")
        return None

async def main():
    """Simple command-line interface"""
    
    print("🤖 SIMPLE CREW INTERFACE")
    print("Just tell me your goal and I'll handle everything!")
    print("-" * 50)
    
    # Get goal from command line args or use default
    import sys
    
    if len(sys.argv) > 1:
        goal = " ".join(sys.argv[1:])
    else:
        # Default goal for demonstration
        goal = "Create a comprehensive user guide for Cyanview RCP remote camera control system"
        print(f"🎯 Using default goal: {goal}")
        print("(To use custom goal: python simple_crew_interface.py 'your goal here')")
    
    if not goal.strip():
        print("❌ Please provide a goal!")
        return
    
    print(f"\n🚀 Starting autonomous crew for: {goal}")
    print("⏳ This will take a few minutes...")
    print()
    
    try:
        # Execute
        result_file = await create_and_run_crew(goal.strip())
        
        if result_file:
            print(f"\n✅ DONE! Check {result_file} for complete results.")
        else:
            print("\n❌ Something went wrong. Check the logs above.")
            
    except KeyboardInterrupt:
        print("\n\n👋 Cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.error(f"Main execution error: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())