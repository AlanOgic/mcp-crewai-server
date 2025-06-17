#!/usr/bin/env python3
"""
Test Evolution Functionality
Watch agents evolve in real-time
"""

import requests
import json
import time
import sys

SERVER_URL = "http://localhost:8080"

def log(message):
    """Print timestamped log message"""
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def create_test_crew():
    """Create a crew specifically for testing evolution"""
    log("🚀 Creating evolution test crew...")
    
    crew_data = {
        "name": "Evolution Test Crew",
        "autonomy_level": "high",
        "description": "A crew designed to test autonomous evolution capabilities",
        "goal": "Demonstrate autonomous evolution and self-improvement"
    }
    
    response = requests.post(f"{SERVER_URL}/api/crews", json=crew_data)
    if response.status_code == 200:
        result = response.json()
        log(f"✅ Crew created: {result['crew_id']}")
        log(f"   Agents: {result['crew_info']['agents_count']}")
        log(f"   Autonomy: {result['crew_info']['autonomy_level']}")
        return result['crew_id']
    else:
        log(f"❌ Failed to create crew: {response.text}")
        return None

def get_crew_status(crew_id):
    """Get detailed crew status"""
    response = requests.get(f"{SERVER_URL}/api/crews/{crew_id}/status")
    if response.status_code == 200:
        return response.json()
    return None

def run_crew(crew_id):
    """Run the crew and capture autonomous decisions"""
    log(f"🏃 Running crew: {crew_id}")
    
    response = requests.post(f"{SERVER_URL}/api/crews/{crew_id.replace(' ', '%20')}/run")
    if response.status_code == 200:
        result = response.json()
        log(f"🧠 Autonomous Decision Made:")
        log(f"   Action: {result.get('decision', {}).get('action', 'Unknown')}")
        log(f"   Reasoning: {result.get('decision', {}).get('reasoning', 'No reasoning provided')}")
        log(f"   Changes: {result.get('decision', {}).get('changes', [])}")
        return result
    else:
        log(f"❌ Failed to run crew: {response.text}")
        return None

def trigger_evolution(crew_id):
    """Force evolution cycle"""
    log(f"🧬 Triggering evolution for crew: {crew_id}")
    
    response = requests.post(f"{SERVER_URL}/api/crews/{crew_id.replace(' ', '%20')}/evolve")
    if response.status_code == 200:
        result = response.json()
        log(f"✨ Evolution Results:")
        for evolution_result in result.get('evolution_results', []):
            log(f"   {evolution_result}")
        return result
    else:
        log(f"❌ Failed to trigger evolution: {response.text}")
        return None

def monitor_agent_changes(crew_id, duration=30):
    """Monitor agent personality changes over time"""
    log(f"👁️  Monitoring agent changes for {duration} seconds...")
    
    initial_status = get_crew_status(crew_id)
    if not initial_status:
        log("❌ Could not get initial status")
        return
    
    log("📊 Initial Agent State:")
    for agent in initial_status.get('agents', []):
        log(f"   Agent {agent['agent_id'][:8]}...")
        log(f"   Role: {agent['role']}")
        log(f"   Evolution Cycles: {agent['evolution_cycles']}")
        log(f"   Personality Traits:")
        for trait, value in agent.get('personality_traits', {}).items():
            log(f"     {trait}: {value:.2f}")
    
    # Wait and check for changes
    time.sleep(duration)
    
    final_status = get_crew_status(crew_id)
    if final_status:
        log("📊 Final Agent State:")
        for agent in final_status.get('agents', []):
            log(f"   Agent {agent['agent_id'][:8]}...")
            log(f"   Role: {agent['role']}")
            log(f"   Evolution Cycles: {agent['evolution_cycles']}")
            log(f"   Personality Traits:")
            for trait, value in agent.get('personality_traits', {}).items():
                log(f"     {trait}: {value:.2f}")

def send_dynamic_instruction(crew_id):
    """Send dynamic instruction to running crew"""
    log("📡 Sending dynamic instruction...")
    
    instruction_data = {
        "crew_id": crew_id,
        "instruction": "Focus on improving collaboration and analytical thinking",
        "priority": "high"
    }
    
    response = requests.post(f"{SERVER_URL}/api/instructions", json=instruction_data)
    if response.status_code == 200:
        log("✅ Dynamic instruction sent successfully")
        return True
    else:
        log(f"❌ Failed to send instruction: {response.text}")
        return False

def main():
    """Main test execution"""
    log("🧪 Starting MCP CrewAI Evolution Test")
    log("=" * 50)
    
    # Step 1: Create test crew
    crew_id = create_test_crew()
    if not crew_id:
        sys.exit(1)
    
    # Step 2: Check initial status
    log("\n📊 Getting initial crew status...")
    initial_status = get_crew_status(crew_id)
    if initial_status:
        log(f"   Formation Date: {initial_status['formation_date']}")
        log(f"   Autonomy Level: {initial_status['autonomy_level']}")
        log(f"   Agents Count: {len(initial_status.get('agents', []))}")
    
    # Step 3: Run crew and see autonomous decision
    log("\n🚀 Testing autonomous decision making...")
    run_result = run_crew(crew_id)
    
    # Step 4: Send dynamic instruction
    log("\n📡 Testing dynamic instructions...")
    send_dynamic_instruction(crew_id)
    
    # Step 5: Trigger evolution
    log("\n🧬 Testing forced evolution...")
    trigger_evolution(crew_id)
    
    # Step 6: Monitor changes
    log("\n👁️  Monitoring for changes...")
    monitor_agent_changes(crew_id, 10)
    
    log("\n✅ Evolution test completed!")
    log(f"🔍 Check logs at: {SERVER_URL}")
    log("🖥️  Monitor with: ./monitor.sh")

if __name__ == "__main__":
    main()