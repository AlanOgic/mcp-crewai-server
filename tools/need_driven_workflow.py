#!/usr/bin/env python3
"""
Need-Driven Research Workflow
Demonstrates how agents research and improve only when they fail at user tasks
"""

import asyncio
import json
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from mcp_crewai.need_driven_evolution import NeedDrivenEvolution, UserRequest, TaskFailure
from mcp_crewai.web_search import WebSearchMCP

async def demonstrate_need_driven_improvement():
    """Demonstrate need-driven improvement cycle"""
    print("🎯 Need-Driven Agent Improvement Demo")
    print("Agents only improve when they fail at user requests")
    print("=" * 60)
    
    # Initialize systems
    evolution_system = NeedDrivenEvolution()
    web_search = WebSearchMCP()
    
    # Set API key
    os.environ['BRAVE_API_KEY'] = 'BSA-A9WmlLLs7Nc2YLkuecCjix11mpN'
    web_search = WebSearchMCP()  # Reinitialize with API key
    
    # Simulate agent with current capabilities
    agent_id = "agent_test_001"
    current_capabilities = {
        "analytical": 0.9,
        "creative": 0.2,      # Low creative skills
        "collaborative": 0.6,
        "decisive": 0.8,
        "technical": 0.4,     # Low technical skills
        "leadership": 0.7
    }
    
    print(f"🤖 Agent Current Capabilities:")
    for skill, level in current_capabilities.items():
        status = "🔴" if level < 0.5 else "🟡" if level < 0.7 else "🟢"
        print(f"   {skill}: {level:.1f} {status}")
    print()
    
    # Scenario 1: User asks for creative design work
    print("📋 Scenario 1: User Request for Creative Design")
    user_query1 = "Create an innovative and visually appealing marketing campaign design for our new product launch"
    
    # Analyze user request
    user_request1 = evolution_system.analyze_user_request(user_query1, "test_crew")
    print(f"   User Query: {user_query1}")
    print(f"   Required Skills: {user_request1.required_skills}")
    print(f"   Complexity: {user_request1.complexity_level}")
    
    # Check capability gaps
    capability_gaps1 = evolution_system.check_capability_gaps(user_request1, current_capabilities)
    print(f"   Capability Gaps: {capability_gaps1}")
    
    if capability_gaps1:
        print("   ❌ Agent cannot handle this request - triggering improvement!")
        
        # Record task failure
        task_failure1 = evolution_system.record_task_failure(
            user_request1, agent_id, 
            "Insufficient creative and design skills",
            ["creative skills below threshold", "design experience needed"]
        )
        
        # Check if research should be triggered
        improvement_need = evolution_system.should_trigger_research(agent_id)
        
        if improvement_need:
            print(f"   🔍 Research triggered for: {improvement_need.skill_gap}")
            print(f"   Priority: {improvement_need.priority}/5")
            
            # Generate research query
            research_query = evolution_system.get_research_query_for_need(improvement_need)
            print(f"   Research Query: {research_query}")
            
            # Conduct web search
            print("   🌐 Searching internet for improvement strategies...")
            search_results = await web_search.web_search(
                query=research_query,
                max_results=5,
                agent_id=agent_id
            )
            
            print(f"   ✅ Found {search_results['result_count']} results")
            for i, result in enumerate(search_results['results'][:2], 1):
                print(f"   {i}. {result['title'][:50]}...")
            
            # Conduct research
            research_results = await web_search.research_topic(
                topic=improvement_need.skill_gap,
                depth="standard",
                agent_id=agent_id
            )
            
            # Validate research relevance
            is_valid = evolution_system.validate_improvement_impact(
                agent_id, improvement_need, research_results
            )
            
            if is_valid:
                print("   ✅ Research addresses user need - creating evolution plan")
                
                # Create evolution plan
                evolution_plan = evolution_system.create_evolution_plan(
                    improvement_need, research_results
                )
                
                print("   🧬 Evolution Plan:")
                print(f"     Target Trait: {evolution_plan['target_trait']}")
                print(f"     Improvement Goal: {evolution_plan['improvement_goal']}")
                print(f"     Expected Gain: +{evolution_plan['expected_improvement']:.2f}")
                print(f"     Trigger: {evolution_plan['trigger_reason']}")
                
                # Simulate evolution
                new_capabilities = current_capabilities.copy()
                new_capabilities[evolution_plan['target_trait']] += evolution_plan['expected_improvement']
                new_capabilities[evolution_plan['target_trait']] = min(1.0, new_capabilities[evolution_plan['target_trait']])
                
                print(f"   📈 Capability Improved:")
                old_val = current_capabilities[evolution_plan['target_trait']]
                new_val = new_capabilities[evolution_plan['target_trait']]
                print(f"     {evolution_plan['target_trait']}: {old_val:.2f} → {new_val:.2f} (+{new_val-old_val:.2f})")
                
                current_capabilities = new_capabilities
            else:
                print("   ⚠️  Research not relevant enough - no evolution triggered")
        else:
            print("   ⏳ No high-priority needs found - waiting for more failures")
    else:
        print("   ✅ Agent can handle this request - no improvement needed")
    
    print()
    
    # Scenario 2: User asks for technical implementation
    print("📋 Scenario 2: User Request for Technical Implementation")
    user_query2 = "Build a complex database optimization system with advanced caching mechanisms"
    
    user_request2 = evolution_system.analyze_user_request(user_query2, "test_crew")
    print(f"   User Query: {user_query2}")
    print(f"   Required Skills: {user_request2.required_skills}")
    print(f"   Complexity: {user_request2.complexity_level}")
    
    capability_gaps2 = evolution_system.check_capability_gaps(user_request2, current_capabilities)
    print(f"   Capability Gaps: {capability_gaps2}")
    
    if capability_gaps2:
        print("   ❌ Agent lacks technical expertise - triggering improvement!")
        
        task_failure2 = evolution_system.record_task_failure(
            user_request2, agent_id,
            "Insufficient technical and system design skills", 
            ["technical skills below expert level", "system architecture knowledge needed"]
        )
        
        improvement_need2 = evolution_system.should_trigger_research(agent_id)
        
        if improvement_need2:
            print(f"   🔍 Research triggered for: {improvement_need2.skill_gap}")
            
            research_query2 = evolution_system.get_research_query_for_need(improvement_need2)
            print(f"   Research Query: {research_query2}")
            
            print("   🌐 Searching for technical improvement strategies...")
            search_results2 = await web_search.web_search(
                query=research_query2,
                max_results=3,
                agent_id=agent_id
            )
            
            print(f"   ✅ Found {search_results2['result_count']} technical resources")
            
            # Continue with research and evolution as in scenario 1...
            research_results2 = await web_search.research_topic(
                topic="technical system design skills",
                depth="comprehensive", 
                agent_id=agent_id
            )
            
            evolution_plan2 = evolution_system.create_evolution_plan(
                improvement_need2, research_results2
            )
            
            print("   🧬 Technical Evolution Plan:")
            print(f"     Focus: {evolution_plan2['improvement_goal']}")
            print(f"     Target: {evolution_plan2['target_trait']} skill enhancement")
    else:
        print("   ✅ Agent has sufficient technical skills")
    
    print()
    
    # Scenario 3: User asks for simple task (no improvement needed)
    print("📋 Scenario 3: User Request for Simple Analysis")
    user_query3 = "Analyze this data and give me a quick summary"
    
    user_request3 = evolution_system.analyze_user_request(user_query3, "test_crew")
    print(f"   User Query: {user_query3}")
    print(f"   Required Skills: {user_request3.required_skills}")
    print(f"   Complexity: {user_request3.complexity_level}")
    
    capability_gaps3 = evolution_system.check_capability_gaps(user_request3, current_capabilities)
    print(f"   Capability Gaps: {capability_gaps3}")
    
    if not capability_gaps3:
        print("   ✅ Agent can handle this perfectly - no research needed!")
        print("   💡 Agent only improves when it faces challenges")
    
    print()
    
    # Show improvement history
    print("📊 Agent Improvement History")
    history = evolution_system.get_improvement_history(agent_id)
    print(f"   Total Task Failures: {history['total_failures']}")
    print(f"   Improvement Needs Identified: {history['improvement_needs']}")
    print(f"   Active Learning Focus: {history['learning_focus']}")
    print(f"   Recent Failure Reasons: {history['recent_failures']}")
    
    print()
    print("🎯 Need-Driven Evolution Summary:")
    print("✅ Agents only research when they fail at user tasks")
    print("✅ Research is targeted to specific capability gaps") 
    print("✅ Evolution directly addresses user needs")
    print("✅ No wasted improvement on unnecessary skills")
    print("✅ Learning is triggered by real challenges")
    
    return {
        "scenarios_tested": 3,
        "improvements_triggered": len([gaps for gaps in [capability_gaps1, capability_gaps2, capability_gaps3] if gaps]),
        "agent_final_capabilities": current_capabilities,
        "improvement_history": history,
        "real_api_used": web_search.use_real_api
    }

if __name__ == "__main__":
    try:
        print("🧠 Need-Driven Agent Improvement System")
        print("   Agents improve only when they fail at user requests")
        print()
        
        results = asyncio.run(demonstrate_need_driven_improvement())
        
        print(f"\n🎉 Demo Complete!")
        print(f"   Scenarios tested: {results['scenarios_tested']}")
        print(f"   Improvements triggered: {results['improvements_triggered']}")
        print(f"   Real web search used: {results['real_api_used']}")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()