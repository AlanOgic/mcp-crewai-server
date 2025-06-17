#!/usr/bin/env python3
"""
Demonstrate the verbose crew execution with Cyanview CI0 FAQ creation
"""

import asyncio
import os
import sys
from datetime import datetime

# Ensure we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def run_verbose_crew_demo():
    """Run a demonstration of verbose crew execution"""
    
    print("🔥 CYANVIEW CI0 FAQ CREATION - VERBOSE CREW DEMONSTRATION")
    print("=" * 80)
    print("👁️  You are about to see:")
    print("   • MAXIMUM VERBOSITY - Every agent conversation")
    print("   • Real-time task execution and decision making")
    print("   • Task termination capabilities (no timeouts)")
    print("   • Results automatically saved to exported_results/")
    print("")
    
    # Use the existing verbose crew execution script
    print("🚀 Running verbose crew execution for Cyanview CI0 FAQ...")
    print("")
    
    # Import and run the verbose execution
    from verbose_crew_execution import verbose_crew_execution
    
    # Run the demonstration
    await verbose_crew_execution()

async def run_real_crewai_demo():
    """Run the real CrewAI execution demonstration"""
    
    print("\n🔥 REAL CREWAI EXECUTION - CYANVIEW FAQ")
    print("=" * 80)
    
    # Import and run real CrewAI execution
    from real_crewai_execution import real_crewai_execution
    
    # Run the real CrewAI demonstration
    await real_crewai_execution()

async def main():
    """Main demonstration"""
    
    # Ensure exported_results directory exists
    os.makedirs('exported_results', exist_ok=True)
    
    print("🎯 Choose your demonstration:")
    print("1. Verbose Crew Execution (MCP Server simulation)")
    print("2. Real CrewAI Execution (Actual CrewAI agents)")
    print("3. Both demonstrations")
    print("")
    
    # For automatic execution, run both
    choice = "3"
    
    if choice in ["1", "3"]:
        try:
            await run_verbose_crew_demo()
        except Exception as e:
            print(f"❌ Verbose crew demo error: {e}")
    
    if choice in ["2", "3"]:
        try:
            await run_real_crewai_demo()
        except Exception as e:
            print(f"❌ Real CrewAI demo error: {e}")
    
    print(f"\n🎉 DEMONSTRATION COMPLETE!")
    print("📁 Check the exported_results/ folder for all generated content")
    print("🔥 Key improvements implemented:")
    print("   ✅ Maximum verbosity - you can see crew working")
    print("   ✅ Task termination instead of timeouts")
    print("   ✅ Results organized in exported_results folder")

if __name__ == "__main__":
    asyncio.run(main())