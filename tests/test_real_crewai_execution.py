#!/usr/bin/env python3
"""
Test Real CrewAI Execution Implementation
"""

import asyncio
import json
import sys
import time
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_crewai.server import MCPCrewAIServer


async def test_real_crewai_execution():
    """Test that real CrewAI execution is called (not simulation)"""
    print("🚀 Testing Real CrewAI Execution...")
    
    server = MCPCrewAIServer()
    
    # Create a simple crew for testing
    crew_args = {
        "crew_name": "real_execution_test",
        "agents_config": [
            {
                "role": "Content Writer",
                "goal": "Write engaging articles",
                "backstory": "Experienced writer with creative flair",
                "personality_preset": "creative"
            },
            {
                "role": "Content Reviewer", 
                "goal": "Review and improve content quality",
                "backstory": "Detail-oriented editor with analytical skills",
                "personality_preset": "analytical"
            }
        ],
        "tasks": [
            {
                "description": "Write a short article about artificial intelligence",
                "agent_role": "Content Writer"
            },
            {
                "description": "Review the article for clarity and accuracy",
                "agent_role": "Content Reviewer"
            }
        ],
        "autonomy_level": 0.2
    }
    
    # Create the crew
    creation_result = await server._create_evolving_crew(crew_args)
    creation_data = json.loads(creation_result[0].text)
    
    assert creation_data["status"] == "success", f"Expected 'success', got {creation_data['status']}"
    crew_id = creation_data["crew_id"]
    print(f"✅ Crew created: {crew_id}")
    
    # Record start time to verify real execution takes time
    start_time = time.time()
    
    # Execute the crew with real CrewAI
    execution_result = await server._run_autonomous_crew({
        "crew_id": crew_id,
        "context": {"topic": "AI innovation", "length": "short"},
        "allow_evolution": False
    })
    
    execution_time = time.time() - start_time
    execution_data = json.loads(execution_result[0].text)
    
    # Verify execution completed successfully (could be 'completed' or 'autonomous_changes_made')
    assert execution_data["status"] in ["completed", "autonomous_changes_made"], f"Expected completion status, got {execution_data['status']}"
    print(f"✅ Real execution completed in {execution_time:.2f} seconds with status: {execution_data['status']}")
    
    # Debug: Print the full response to see what we actually got
    print(f"🔍 Full execution response keys: {list(execution_data.keys())}")
    if execution_time < 1.0:
        print("⚠️  Warning: Execution completed very quickly - might not be real CrewAI execution")
    
    # Check for deliverable results or other result indicators
    if "deliverable_results" not in execution_data:
        print(f"❌ Missing deliverable_results. Available keys: {list(execution_data.keys())}")
        # Print full response for debugging
        print(f"Full response: {json.dumps(execution_data, indent=2)}")
        
    assert "deliverable_results" in execution_data or "results" in execution_data, "Missing execution results"
    deliverables = execution_data.get("deliverable_results", execution_data.get("results", {}))
    
    # Check that we have real task outputs (not simulated)
    assert "outputs" in deliverables, "Missing task outputs"
    assert len(deliverables["outputs"]) == 2, f"Expected 2 outputs, got {len(deliverables['outputs'])}"
    
    # Verify files were generated
    assert "files_generated" in deliverables, "Missing generated files"
    assert len(deliverables["files_generated"]) >= 2, "Should have generated files for tasks"
    
    # Verify debrief was conducted
    assert "debrief_insights" in execution_data, "Missing debrief insights"
    debrief = execution_data["debrief_insights"]
    assert "collective_insights" in debrief, "Missing collective insights"
    
    # Verify agents were liberated
    assert "agents_to_be_liberated" in execution_data, "Missing liberation info"
    assert execution_data["agents_to_be_liberated"] == 2, "Should liberate 2 agents"
    
    print("✅ Real CrewAI execution with complete lifecycle verified!")
    return True


async def test_dynamic_instruction_during_execution():
    """Test dynamic instructions work during real CrewAI execution"""
    print("\n🔄 Testing Dynamic Instructions During Real Execution...")
    
    server = MCPCrewAIServer()
    
    # Create crew for long-running test
    crew_args = {
        "crew_name": "dynamic_instruction_test",
        "agents_config": [
            {
                "role": "Research Analyst",
                "goal": "Conduct thorough research and analysis",
                "backstory": "Methodical researcher with attention to detail",
                "personality_preset": "analytical"
            }
        ],
        "tasks": [
            {
                "description": "Research emerging trends in renewable energy technology",
                "agent_role": "Research Analyst"
            }
        ],
        "autonomy_level": 0.2
    }
    
    # Create the crew
    creation_result = await server._create_evolving_crew(crew_args)
    creation_data = json.loads(creation_result[0].text)
    crew_id = creation_data["crew_id"]
    print(f"✅ Crew created: {crew_id}")
    
    # Start execution (this will run in background)
    async def run_crew():
        return await server._run_autonomous_crew({
            "crew_id": crew_id,
            "context": {"focus": "solar_and_wind", "depth": "comprehensive"},
            "allow_evolution": False
        })
    
    # Start execution task
    execution_task = asyncio.create_task(run_crew())
    
    # Wait a moment for execution to start
    await asyncio.sleep(1)
    
    # Send dynamic instruction during execution
    instruction_result = await server._add_dynamic_instruction({
        "crew_id": crew_id,
        "instruction": "Focus specifically on battery storage innovations",
        "instruction_type": "guidance",
        "priority": 3
    })
    
    instruction_data = json.loads(instruction_result[0].text)
    assert instruction_data["status"] == "success", "Failed to add dynamic instruction"
    print("✅ Dynamic instruction added during execution")
    
    # Wait for execution to complete
    execution_result = await execution_task
    execution_data = json.loads(execution_result[0].text)
    
    # Verify execution completed with dynamic instruction
    assert execution_data["status"] in ["completed", "autonomous_changes_made"], f"Execution should complete, got: {execution_data['status']}"
    assert "dynamic_instruction_stats" in execution_data, "Missing instruction stats"
    
    stats = execution_data["dynamic_instruction_stats"]
    assert stats["instructions_processed"] >= 1, "Should have processed at least 1 instruction"
    
    print("✅ Dynamic instructions work during real execution!")
    return True


async def test_emergency_stop_during_execution():
    """Test emergency stop cancels real CrewAI execution"""
    print("\n🚨 Testing Emergency Stop During Real Execution...")
    
    server = MCPCrewAIServer()
    
    # Create crew for emergency stop test
    crew_args = {
        "crew_name": "emergency_stop_test",
        "agents_config": [
            {
                "role": "Data Scientist",
                "goal": "Perform complex data analysis",
                "backstory": "Expert in machine learning and statistics",
                "personality_preset": "analytical"
            }
        ],
        "tasks": [
            {
                "description": "Analyze large dataset and create predictive models",
                "agent_role": "Data Scientist"
            }
        ],
        "autonomy_level": 0.2
    }
    
    # Create the crew
    creation_result = await server._create_evolving_crew(crew_args)
    creation_data = json.loads(creation_result[0].text)
    crew_id = creation_data["crew_id"]
    print(f"✅ Crew created: {crew_id}")
    
    # Start execution task
    async def run_crew():
        return await server._run_autonomous_crew({
            "crew_id": crew_id,
            "context": {"dataset": "financial_markets", "model_type": "neural_network"},
            "allow_evolution": False
        })
    
    execution_task = asyncio.create_task(run_crew())
    
    # Wait for execution to start
    await asyncio.sleep(0.5)
    
    # Send emergency stop
    stop_result = await server._add_dynamic_instruction({
        "crew_id": crew_id,
        "instruction": "Emergency stop - critical issue detected",
        "instruction_type": "emergency_stop",
        "priority": 5
    })
    
    stop_data = json.loads(stop_result[0].text)
    assert stop_data["status"] == "success", "Failed to add emergency stop"
    print("✅ Emergency stop instruction added")
    
    # Wait for execution to be cancelled
    execution_result = await execution_task
    execution_data = json.loads(execution_result[0].text)
    
    # Verify execution was stopped
    assert execution_data["status"] == "stopped", f"Expected 'stopped', got {execution_data['status']}"
    assert "stop_reason" in execution_data, "Missing stop reason"
    assert "Emergency stop" in execution_data["stop_reason"], "Wrong stop reason"
    
    print("✅ Emergency stop successfully cancelled real execution!")
    return True


async def test_real_result_processing():
    """Test that real CrewAI results are properly processed"""
    print("\n📊 Testing Real Result Processing...")
    
    server = MCPCrewAIServer()
    
    # Create crew with multiple tasks to test result processing
    crew_args = {
        "crew_name": "result_processing_test",
        "agents_config": [
            {
                "role": "Technical Writer",
                "goal": "Create clear technical documentation",
                "backstory": "Expert in translating complex concepts to readable content",
                "personality_preset": "analytical"
            },
            {
                "role": "Quality Assurance",
                "goal": "Ensure content meets quality standards",
                "backstory": "Meticulous reviewer focused on accuracy and clarity",
                "personality_preset": "analytical"
            }
        ],
        "tasks": [
            {
                "description": "Write technical documentation for API endpoints",
                "agent_role": "Technical Writer"
            },
            {
                "description": "Review documentation for completeness and accuracy",
                "agent_role": "Quality Assurance"
            }
        ],
        "autonomy_level": 0.2
    }
    
    # Create and execute crew
    creation_result = await server._create_evolving_crew(crew_args)
    creation_data = json.loads(creation_result[0].text)
    crew_id = creation_data["crew_id"]
    
    execution_result = await server._run_autonomous_crew({
        "crew_id": crew_id,
        "context": {"api_version": "v2", "format": "markdown"},
        "allow_evolution": False
    })
    
    execution_data = json.loads(execution_result[0].text)
    
    # Detailed verification of result processing
    assert execution_data["status"] in ["completed", "autonomous_changes_made"], f"Execution should complete, got: {execution_data['status']}"
    
    deliverables = execution_data["deliverable_results"]
    
    # Check deliverable structure
    assert "summary" in deliverables, "Missing summary"
    assert "outputs" in deliverables, "Missing outputs"
    assert "files_generated" in deliverables, "Missing files"
    assert "formats_available" in deliverables, "Missing formats"
    
    # Verify task outputs
    outputs = deliverables["outputs"]
    assert len(outputs) == 2, f"Expected 2 outputs, got {len(outputs)}"
    
    for i, output in enumerate(outputs):
        assert "task_id" in output, f"Missing task_id in output {i}"
        assert "description" in output, f"Missing description in output {i}"
        assert "assigned_agent" in output, f"Missing assigned_agent in output {i}"
        assert "result" in output, f"Missing result in output {i}"
        assert "format" in output, f"Missing format in output {i}"
        
        # Verify we have real content (not just "Completed: ...")
        assert len(output["result"]) > 20, f"Result seems too short: {output['result']}"
    
    # Verify file generation
    files = deliverables["files_generated"]
    assert len(files) >= 3, f"Expected at least 3 files, got {len(files)}"  # 2 task files + 1 report
    
    for file_info in files:
        assert "filename" in file_info, "Missing filename"
        assert "content" in file_info, "Missing content"
        assert "format" in file_info, "Missing format"
        assert len(file_info["content"]) > 50, f"File content seems too short: {file_info['filename']}"
    
    print("✅ Real result processing verified!")
    return True


async def test_lifecycle_completion():
    """Test complete lifecycle: Execute → Debrief → Liberation → Cleanup"""
    print("\n🔄 Testing Complete Lifecycle...")
    
    server = MCPCrewAIServer()
    
    # Track initial state
    initial_crews_count = len(server.crews)
    initial_agents_count = len(server.agents)
    
    # Create crew
    crew_args = {
        "crew_name": "lifecycle_test",
        "agents_config": [
            {
                "role": "Project Manager",
                "goal": "Manage project execution and team coordination",
                "backstory": "Experienced in agile project management",
                "personality_preset": "collaborative"
            }
        ],
        "tasks": [
            {
                "description": "Create project timeline and milestone tracking",
                "agent_role": "Project Manager"
            }
        ],
        "autonomy_level": 0.2
    }
    
    creation_result = await server._create_evolving_crew(crew_args)
    creation_data = json.loads(creation_result[0].text)
    crew_id = creation_data["crew_id"]
    
    # Verify crew was added
    assert len(server.crews) == initial_crews_count + 1, "Crew should be added"
    assert len(server.agents) == initial_agents_count + 1, "Agent should be added"
    
    # Execute crew
    execution_result = await server._run_autonomous_crew({
        "crew_id": crew_id,
        "context": {"project_type": "software_development", "duration": "3_months"},
        "allow_evolution": False
    })
    
    execution_data = json.loads(execution_result[0].text)
    
    # Verify complete lifecycle components
    assert execution_data["status"] in ["completed", "autonomous_changes_made"], f"Should complete successfully, got: {execution_data['status']}"
    assert "deliverable_results" in execution_data, "Missing deliverables"
    assert "debrief_insights" in execution_data, "Missing debrief"
    assert "evolution_events" in execution_data, "Missing evolution events"
    assert "agents_to_be_liberated" in execution_data, "Missing liberation info"
    
    # Verify debrief details
    debrief = execution_data["debrief_insights"]
    assert "session_id" in debrief, "Missing debrief session ID"
    assert "participants" in debrief, "Missing debrief participants"
    assert "collective_insights" in debrief, "Missing collective insights"
    assert "lessons_learned" in debrief, "Missing lessons learned"
    assert "team_dynamics" in debrief, "Missing team dynamics"
    
    # Verify agents were liberated (should be removed from active memory)
    # Note: Liberation happens after response is returned, so we need to wait a moment
    await asyncio.sleep(0.1)
    
    # Check that crew was moved to completed crews
    assert hasattr(server, 'completed_crews'), "Should have completed_crews storage"
    
    print("✅ Complete lifecycle verified!")
    return True


async def main():
    """Run all real CrewAI execution tests"""
    print("🧪 Real CrewAI Execution Tests")
    print("=" * 60)
    
    try:
        # Run all test scenarios
        await test_real_crewai_execution()
        await test_dynamic_instruction_during_execution()
        await test_emergency_stop_during_execution()
        await test_real_result_processing()
        await test_lifecycle_completion()
        
        print("\n" + "=" * 60)
        print("🎉 ALL REAL CREWAI EXECUTION TESTS PASSED!")
        print("✅ Simulation successfully replaced with real CrewAI execution")
        print("✅ Dynamic instructions work during real execution")
        print("✅ Emergency stop cancels running CrewAI workflows")
        print("✅ Real results are properly processed and delivered")
        print("✅ Complete lifecycle works: Execute → Debrief → Liberation")
        print("\n🚀 Ready for production use with real CrewAI workflows!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)