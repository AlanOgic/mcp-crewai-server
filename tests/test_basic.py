#!/usr/bin/env python3
"""
Basic test for MCP CrewAI Server
"""

import asyncio
import sys
from mcp_crewai.server import MCPCrewAIServer

async def test_server_creation():
    """Test server creation and basic functionality"""
    print("🚀 Testing MCP CrewAI Server Creation...")
    
    # Create server instance
    server = MCPCrewAIServer()
    print("✅ Server instance created successfully!")
    
    # Test server properties
    print(f"📊 Server name: {server.server.name}")
    print(f"🧠 Evolution engine initialized: {server.evolution_engine is not None}")
    print(f"🔄 Instruction handler initialized: {server.instruction_handler is not None}")
    print(f"👥 Crews storage: {type(server.crews)}")
    print(f"🤖 Agents storage: {type(server.agents)}")
    
    return True

async def test_personality_templates():
    """Test personality templates application"""
    print("\n🎭 Testing Personality Templates...")
    
    server = MCPCrewAIServer()
    
    # Create a test agent with analytical preset
    from mcp_crewai.mcp_client_agent import MCPClientAgent
    
    agent = MCPClientAgent(
        role="Test Analyst",
        goal="Test goal", 
        backstory="Test backstory",
        verbose=False
    )
    
    # Apply analytical preset
    server._apply_personality_preset(agent, "analytical")
    
    # Check traits
    analytical_trait = agent.personality_traits["analytical"].value
    creative_trait = agent.personality_traits["creative"].value
    
    print(f"📈 Analytical trait: {analytical_trait}")
    print(f"🎨 Creative trait: {creative_trait}")
    
    assert analytical_trait > creative_trait, "Analytical should be higher than creative for analytical preset"
    print("✅ Personality template application works!")
    
    return True

async def test_evolution_engine():
    """Test evolution engine functionality"""
    print("\n🧬 Testing Evolution Engine...")
    
    server = MCPCrewAIServer()
    engine = server.evolution_engine
    
    # Test evolution strategies
    strategies = engine.evolution_strategies
    print(f"🎯 Available evolution strategies: {len(strategies)}")
    for strategy in strategies:
        print(f"  - {strategy}: {strategies[strategy]['description']}")
    
    print("✅ Evolution engine initialized with strategies!")
    
    return True

async def test_dynamic_instructions():
    """Test dynamic instruction handler"""
    print("\n🔄 Testing Dynamic Instructions...")
    
    server = MCPCrewAIServer()
    handler = server.instruction_handler
    
    # Add a test instruction
    instruction_id = handler.add_instruction(
        content="Test guidance instruction",
        instruction_type="guidance",
        target="test_crew"
    )
    
    print(f"📝 Added instruction with ID: {instruction_id}")
    
    # Get instruction status
    status = handler.get_instruction_status(instruction_id)
    print(f"📊 Instruction status: {status['processed']}")
    
    print("✅ Dynamic instructions system works!")
    
    return True

async def main():
    """Run all tests"""
    print("🧪 MCP CrewAI Server - Basic Tests")
    print("=" * 50)
    
    try:
        await test_server_creation()
        await test_personality_templates()
        await test_evolution_engine()
        await test_dynamic_instructions()
        
        print("\n" + "=" * 50)
        print("🎉 ALL BASIC TESTS PASSED!")
        print("🚀 MCP CrewAI Server is ready for revolutionary AI collaboration!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)