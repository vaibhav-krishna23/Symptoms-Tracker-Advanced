"""FastMCP Client for LangGraph Integration"""
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from typing import Any
import os

class FastMCPClient:
    """Client for FastMCP server using stdio transport"""
    
    def __init__(self, server_script_path: str):
        self.server_script_path = os.path.abspath(server_script_path)
        self.session = None
        self.client = None
    
    async def __aenter__(self):
        """Start MCP server and establish connection"""
        server_params = StdioServerParameters(
            command="python",
            args=[self.server_script_path],
            env=None
        )
        
        self.client = stdio_client(server_params)
        self.read, self.write = await self.client.__aenter__()
        self.session = ClientSession(self.read, self.write)
        await self.session.__aenter__()
        
        # Initialize session
        await self.session.initialize()
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close MCP connection"""
        if self.session:
            await self.session.__aexit__(exc_type, exc_val, exc_tb)
        if self.client:
            await self.client.__aexit__(exc_type, exc_val, exc_tb)
    
    async def call_tool(self, tool_name: str, **kwargs) -> Any:
        """Call MCP tool and return result"""
        result = await self.session.call_tool(tool_name, arguments=kwargs)
        return result.content[0].text if result.content else {}
    
    async def list_tools(self) -> list:
        """List available MCP tools"""
        tools = await self.session.list_tools()
        return tools.tools
