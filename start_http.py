#!/usr/bin/env python3
"""
Start MCP CrewAI Server in HTTP mode for monitoring and external access
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.mcp_crewai.server import MCPCrewAIServer
from src.mcp_crewai.http_server import MCPHTTPServer
from src.mcp_crewai.config import get_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Main entry point for HTTP server"""
    logger.info("🚀 Starting MCP CrewAI Server in HTTP mode...")
    
    try:
        # Redirect stdout/stderr to prevent CrewAI FilteredStream errors
        import io
        import contextlib
        
        # Create safe streams that won't cause flush errors
        safe_stdout = io.StringIO()
        safe_stderr = io.StringIO()
        
        with contextlib.redirect_stdout(safe_stdout), contextlib.redirect_stderr(safe_stderr):
            # Load configuration
            config = get_config()
            
            # Create MCP server instance (without stdio)
            mcp_server = MCPCrewAIServer()
            
            # Start background evolution
            await mcp_server.start_background_evolution()
        
        # Restore normal stdout/stderr after initialization
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        
        # Create HTTP server
        http_server = MCPHTTPServer(mcp_server)
        
        # Start HTTP server
        await http_server.run(
            host=config.mcp_server_host,
            port=config.mcp_server_port
        )
        
    except KeyboardInterrupt:
        logger.info("🛑 Server shutdown requested by user")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())