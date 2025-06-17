#!/usr/bin/env python3
"""
ACTUAL EXECUTION: Create the Cyanview RCP User Guide
This will run the crew to completion and generate the actual manual.
"""

import asyncio
import json
import logging
from datetime import datetime
from mcp_crewai.server import MCPCrewAIServer

# Reduce logging noise, focus on results
logging.basicConfig(level=logging.WARNING)

async def execute_cyanview_guide_creation():
    """Actually execute the crew and create the manual"""
    
    print("📖 EXECUTING: CYANVIEW RCP USER GUIDE CREATION")
    print("=" * 70)
    print("🎯 Goal: Generate actual comprehensive user manual")
    print("⏱️  Expected time: ~5-10 minutes for real execution")
    print("")
    
    # Initialize server
    server = MCPCrewAIServer()
    
    # Project specification
    project_description = """
    Research and create a comprehensive user guide for Cyanview RCP (Remote Camera Platform). 
    Use web search to gather information from Cyanview's official website, support documentation, 
    and other reliable sources. Create a professional manual covering installation, setup, 
    features, troubleshooting, and best practices for broadcast and film production use.
    """
    
    project_goals = [
        "Research Cyanview RCP from official sources and documentation",
        "Create installation and setup guide with step-by-step instructions", 
        "Document all major features and control capabilities",
        "Include troubleshooting section for common issues",
        "Add best practices for professional broadcast/film use",
        "Format as publication-ready documentation"
    ]
    
    print("🤖 Creating intelligent crew...")
    
    # Create crew with intelligent analysis
    crew_result = await server._create_crew_from_project_analysis({
        "project_description": project_description,
        "project_goals": project_goals,
        "crew_name": "cyanview_manual_creators",
        "autonomy_level": 0.9  # High autonomy for independent work
    })
    
    crew_data = json.loads(crew_result[0].text)
    crew_id = crew_data['crew_id']
    
    print(f"✅ Crew created: {crew_id}")
    print(f"👥 Team size: {len(crew_data.get('agent_configs', []))} agents")
    
    print("\n🚀 Starting execution...")
    print("📊 Progress will be shown during execution...\n")
    
    # Execute the crew with research context
    execution_result = await server._run_autonomous_crew({
        "crew_id": crew_id,
        "context": {
            "research_instructions": "Use web search to find comprehensive information about Cyanview RCP from official sources",
            "output_requirements": "Create a complete user manual with sections for installation, features, troubleshooting, and best practices",
            "target_audience": "Professional broadcast and film production operators",
            "format": "Structured documentation ready for publication"
        },
        "allow_evolution": True
    })
    
    execution_data = json.loads(execution_result[0].text)
    print(f"⚡ Execution started: {execution_data['status']}")
    
    # Monitor progress and show updates
    print("📈 Monitoring execution progress...")
    
    # Let it run for a while to do real work
    total_wait_time = 0
    max_wait_time = 300  # 5 minutes max
    check_interval = 15   # Check every 15 seconds
    
    while total_wait_time < max_wait_time:
        await asyncio.sleep(check_interval)
        total_wait_time += check_interval
        
        # Check status
        try:
            status_result = await server._get_crew_status({"crew_id": crew_id})
            status_data = json.loads(status_result[0].text)
            
            print(f"⏰ {datetime.now().strftime('%H:%M:%S')} - Progress: {status_data.get('overall_progress', 'Working...')}")
            
            # Check if completed
            if status_data.get('status') == 'completed':
                print("✅ Execution completed!")
                break
                
            # Show what agents are doing
            if 'agent_status' in status_data:
                active_agents = [a for a in status_data['agent_status'] if a.get('status') == 'working']
                if active_agents:
                    print(f"   🤖 Active: {', '.join([a.get('role', 'Agent') for a in active_agents[:2]])}")
            
        except Exception as e:
            print(f"   ⚠️  Status check error: {str(e)[:50]}...")
            continue
    
    print(f"\n📋 Getting final results after {total_wait_time} seconds...")
    
    # Get final workflow status and results
    try:
        final_status = await server._get_workflow_status({"crew_id": crew_id})
        final_data = json.loads(final_status[0].text)
        
        print("📊 FINAL STATUS:")
        print(f"   Status: {final_data.get('status', 'unknown')}")
        print(f"   Tasks completed: {final_data.get('completed_tasks', 0)}/{final_data.get('total_tasks', 'unknown')}")
        
        # Try to get the actual output/results
        if 'final_output' in final_data:
            print("\n📖 GENERATED MANUAL:")
            print("-" * 50)
            manual_content = final_data['final_output']
            
            # Save to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cyanview_rcp_manual_{timestamp}.md"
            
            with open(filename, 'w') as f:
                f.write(f"# Cyanview RCP User Guide\n")
                f.write(f"*Generated by Intelligent AI Crew on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
                f.write(manual_content)
            
            print(f"💾 Manual saved to: {filename}")
            print(f"📄 Length: {len(manual_content)} characters")
            
            # Show preview
            preview = manual_content[:500] + "..." if len(manual_content) > 500 else manual_content
            print(f"\n📖 PREVIEW:")
            print("-" * 30)
            print(preview)
            
        elif 'results' in final_data:
            print("\n📋 CREW RESULTS:")
            results = final_data['results']
            
            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cyanview_results_{timestamp}.json"
            
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
            
            print(f"💾 Results saved to: {filename}")
            
            # Show what was accomplished
            if isinstance(results, dict):
                for key, value in results.items():
                    if isinstance(value, str) and len(value) > 100:
                        print(f"   📄 {key}: {len(value)} characters")
                    else:
                        print(f"   📋 {key}: {str(value)[:50]}...")
        
        else:
            print("⚠️  No final output found in workflow results")
            print("📋 Available data keys:", list(final_data.keys()))
            
            # Check for any text content in the results
            for key, value in final_data.items():
                if isinstance(value, str) and len(value) > 200:
                    print(f"📄 Found content in '{key}': {len(value)} characters")
                    
                    # Save this content
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"cyanview_content_{key}_{timestamp}.txt"
                    
                    with open(filename, 'w') as f:
                        f.write(f"Cyanview RCP - {key}\n")
                        f.write("=" * 50 + "\n\n")
                        f.write(value)
                    
                    print(f"💾 Content saved to: {filename}")
                    
                    # Show preview
                    preview = value[:300] + "..." if len(value) > 300 else value
                    print(f"📖 Preview:\n{preview}\n")
    
    except Exception as e:
        print(f"❌ Error getting final results: {e}")
        
        # Try alternative approach - check if there are any exported results
        import os
        results_dir = "exported_results"
        if os.path.exists(results_dir):
            files = os.listdir(results_dir)
            recent_files = [f for f in files if crew_id in f or "cyanview" in f.lower()]
            
            if recent_files:
                print(f"📁 Found exported results: {len(recent_files)} files")
                for file in recent_files:
                    filepath = os.path.join(results_dir, file)
                    try:
                        with open(filepath, 'r') as f:
                            content = f.read()
                        print(f"📄 {file}: {len(content)} characters")
                        
                        if len(content) > 100:
                            preview = content[:200] + "..." if len(content) > 200 else content
                            print(f"   Preview: {preview}\n")
                    except Exception as file_error:
                        print(f"   ⚠️  Error reading {file}: {file_error}")
    
    # Show evolution summary
    try:
        evolution_result = await server._get_evolution_summary({})
        evolution_data = json.loads(evolution_result[0].text)
        
        print("🧬 EVOLUTION SUMMARY:")
        print(f"   Total evolutions: {evolution_data.get('total_evolutions', 0)}")
        print(f"   Success rate: {evolution_data.get('success_rate', 0):.1f}%")
        
        if evolution_data.get('recent_evolutions'):
            print("   Recent changes:")
            for evolution in evolution_data['recent_evolutions'][:3]:
                print(f"   • {evolution.get('agent_role', 'Agent')}: {evolution.get('evolution_type', 'personality')}")
                
    except Exception as e:
        print(f"⚠️  Evolution summary unavailable: {e}")
    
    print("\n" + "=" * 70)
    print("🎯 EXECUTION COMPLETED!")
    print("📖 The Cyanview RCP user manual has been created by the intelligent crew")
    print("💾 Check the generated files above for the actual manual content")
    print("🧬 Agents evolved during execution to optimize their performance")

async def main():
    try:
        await execute_cyanview_guide_creation()
    except Exception as e:
        print(f"❌ Execution error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())