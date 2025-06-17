#!/usr/bin/env python3
"""
MCP CrewAI Server - Main Entry Point
Real user-driven crew execution with Agent 1 building the crew
"""

import sys
import os

def main():
    """Main entry point - choose execution mode"""
    
    print("🔥 MCP CREWAI SERVER")
    print("=" * 50)
    print("Choose execution mode:")
    print("1. Crew Builder (Agent 1 designs crew)")
    print("2. MCP Server (Start MCP server)")
    print("3. Examples (Run example scripts)")
    print("")
    
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
    else:
        try:
            mode = input("Enter choice (1-3): ").strip()
        except (EOFError, KeyboardInterrupt):
            mode = "1"  # Default to crew builder
    
    if mode in ["1", "crew", "builder"]:
        # Run crew builder
        goal_args = sys.argv[2:] if len(sys.argv) > 2 else []
        if goal_args:
            goal = " ".join(goal_args)
            os.system(f'python3 crew_builder.py "{goal}"')
        else:
            os.system('python3 crew_builder.py')
            
    elif mode in ["2", "server", "mcp"]:
        # Start MCP server
        from src.mcp_crewai.server import main as server_main
        server_main()
        
    elif mode in ["3", "examples", "demo"]:
        # Show examples
        print("\n📁 Available examples:")
        print("- examples/verbose_crew_execution.py")
        print("- examples/simple_crew_interface.py") 
        print("- tools/real_crewai_execution.py")
        print("\nRun: python3 examples/<script_name>")
        
    else:
        print("❌ Invalid choice. Using crew builder...")
        os.system('python3 crew_builder.py')

if __name__ == "__main__":
    main()