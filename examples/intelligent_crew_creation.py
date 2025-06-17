#!/usr/bin/env python3
"""
Example: Intelligent Crew Creation with Project Analysis

This example demonstrates how the new Project Analysis Agent works:
1. Analyzes project requirements to determine complexity and domain
2. Automatically recommends optimal number and types of agents
3. Creates a perfectly-sized crew for the specific project

No more guessing how many agents you need!
"""

import asyncio
import json
from mcp_crewai.project_analyzer import ProjectAnalyzer

async def demonstrate_intelligent_crew_creation():
    """Demonstrate the new intelligent crew creation capabilities"""
    
    analyzer = ProjectAnalyzer()
    
    print("🧠 Intelligent Project Analysis & Crew Creation Demo")
    print("=" * 60)
    
    # Example 1: Software Development Project
    print("\n📱 Example 1: Mobile App Development")
    print("-" * 40)
    
    software_project = """
    Develop a comprehensive mobile application for food delivery with real-time tracking, 
    payment integration, user reviews, restaurant management dashboard, and AI-powered 
    recommendation system. The app needs to support iOS and Android platforms, handle 
    high traffic loads, integrate with multiple payment gateways, and provide analytics 
    for business insights.
    """
    
    goals = [
        "Launch MVP within 3 months",
        "Support 10,000+ concurrent users",
        "Achieve 99.9% uptime",
        "Implement advanced security features"
    ]
    
    analysis = await analyzer.analyze_project(
        project_description=software_project,
        project_goals=goals,
        constraints={"max_agents": 8}
    )
    
    print(f"📊 Analysis Results:")
    print(f"   • Complexity: {analysis.complexity.value}")
    print(f"   • Domain: {analysis.domain.value}")
    print(f"   • Recommended Agents: {analysis.recommended_agent_count}")
    print(f"   • Confidence: {analysis.confidence_score:.2f}")
    print(f"   • Duration: {analysis.estimated_duration}")
    print(f"\n💡 Reasoning: {analysis.reasoning}")
    
    print(f"\n👥 Recommended Team Composition:")
    for i, agent in enumerate(analysis.recommended_agents, 1):
        print(f"   {i}. {agent['role']} - {agent['personality_preset']}")
        print(f"      Goal: {agent['goal'][:60]}...")
    
    # Example 2: Content Marketing Project  
    print("\n\n📝 Example 2: Content Marketing Campaign")
    print("-" * 40)
    
    marketing_project = """
    Create a comprehensive content marketing strategy for a B2B SaaS startup launching 
    a new project management tool. Need to develop thought leadership content, SEO-optimized 
    blog posts, social media campaigns, email marketing sequences, and lead magnets. 
    Target audience includes project managers, team leads, and small business owners.
    """
    
    marketing_goals = [
        "Generate 1000+ qualified leads per month",
        "Achieve top 3 search ranking for target keywords",
        "Build social media following of 10K+",
        "Create 50+ pieces of evergreen content"
    ]
    
    analysis2 = await analyzer.analyze_project(
        project_description=marketing_project,
        project_goals=marketing_goals,
        constraints={"max_agents": 5}
    )
    
    print(f"📊 Analysis Results:")
    print(f"   • Complexity: {analysis2.complexity.value}")
    print(f"   • Domain: {analysis2.domain.value}")
    print(f"   • Recommended Agents: {analysis2.recommended_agent_count}")
    print(f"   • Confidence: {analysis2.confidence_score:.2f}")
    print(f"   • Duration: {analysis2.estimated_duration}")
    
    print(f"\n👥 Recommended Team Composition:")
    for i, agent in enumerate(analysis2.recommended_agents, 1):
        print(f"   {i}. {agent['role']} - {agent['personality_preset']}")
        print(f"      Goal: {agent['goal'][:60]}...")
    
    # Example 3: Simple vs Complex Project Comparison
    print("\n\n🔄 Example 3: Simple vs Complex Project Comparison")
    print("-" * 50)
    
    simple_project = "Write a blog post about Python best practices"
    complex_project = """
    Build an enterprise-grade distributed microservices architecture for a global 
    e-commerce platform with real-time inventory management, fraud detection, 
    multi-currency support, AI-powered personalization, advanced analytics, 
    and integration with 50+ third-party services across 20 countries.
    """
    
    simple_analysis = await analyzer.analyze_project(simple_project)
    complex_analysis = await analyzer.analyze_project(complex_project)
    
    print(f"📝 Simple Project: {simple_analysis.recommended_agent_count} agents ({simple_analysis.complexity.value})")
    print(f"🏗️  Complex Project: {complex_analysis.recommended_agent_count} agents ({complex_analysis.complexity.value})")
    
    print("\n" + "=" * 60)
    print("✨ Key Benefits of Intelligent Crew Creation:")
    print("   • No more guessing optimal team size")
    print("   • Automatic domain expertise matching")
    print("   • Complexity-aware agent allocation")
    print("   • Role specialization based on project needs")
    print("   • Confidence scoring for reliability")
    print("   • Reasoning explanations for transparency")
    
    print("\n🚀 To use in your application:")
    print("""
    # Just describe your project - the AI figures out the rest!
    
    crew_data = await mcp_client.call_tool(
        "create_crew_from_project_analysis",
        {
            "project_description": "Your project description here...",
            "project_goals": ["Goal 1", "Goal 2", "Goal 3"],
            "crew_name": "my_intelligent_crew",
            "constraints": {"max_agents": 6}
        }
    )
    
    # Or just get analysis without creating crew:
    analysis = await mcp_client.call_tool(
        "analyze_project_requirements", 
        {"project_description": "Your project description here..."}
    )
    """)

if __name__ == "__main__":
    asyncio.run(demonstrate_intelligent_crew_creation())